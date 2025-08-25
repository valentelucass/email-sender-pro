import time
import smtplib
import re
import mimetypes
from pathlib import Path
import random
import base64
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from .config import EMAIL, SMTP_USER, SENHA, SMTP_SERVER, SMTP_PORT, FROM_NAME, REPLY_TO, SEND_INTERVAL, LIST_UNSUBSCRIBE, TEXT_ONLY, DEBUG_SMTP
from .config import MAILJET_API_KEY, MAILJET_API_SECRET, USE_MAILJET_API


def _send_via_mailjet_api(
    destino: str,
    assunto: str,
    corpo: str,
    anexos: list[str | Path] | None = None,
    html: str | None = None,
    *,
    from_email: str,
    from_name: str | None,
    reply_to: str | None,
) -> bool:
    """Envia e-mail usando a API HTTP do Mailjet.

    Docs: https://dev.mailjet.com/email/guides/send-api-v31/
    """
    if not MAILJET_API_KEY or not MAILJET_API_SECRET:
        print("[Mailjet API] MAILJET_API_KEY/MAILJET_API_SECRET não configurados.")
        return False

    msg = {
        "From": {
            "Email": from_email,
            "Name": (from_name or "").strip() or from_email,
        },
        "To": [{"Email": destino}],
        "Subject": assunto,
        "TextPart": corpo or "",
    }
    if html and not TEXT_ONLY:
        msg["HTMLPart"] = html

    headers = {}
    if reply_to:
        headers["Reply-To"] = reply_to
    if LIST_UNSUBSCRIBE:
        headers["List-Unsubscribe"] = LIST_UNSUBSCRIBE
    if headers:
        msg["Headers"] = headers

    # Anexos
    attachments = []
    if anexos:
        for path in anexos:
            if not path:
                continue
            p = Path(path)
            if not p.exists() or not p.is_file():
                print(f"Anexo não encontrado, ignorado: {p}")
                continue
            ctype, encoding = mimetypes.guess_type(str(p))
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            with open(p, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('ascii')
            attachments.append({
                "ContentType": ctype,
                "Filename": p.name,
                "Base64Content": b64,
            })
    if attachments:
        msg["Attachments"] = attachments

    payload = {"Messages": [msg]}

    try:
        resp = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
            json=payload,
            timeout=30,
        )
        if DEBUG_SMTP:
            print(f"[Mailjet API] Status: {resp.status_code} Body: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        # Verifica se houve falhas
        messages = data.get("Messages", [])
        if not messages:
            print("[Mailjet API] Resposta sem 'Messages'.")
            return False
        status = messages[0].get("Status")
        if status and status.lower() == "success":
            print(f"E-mail enviado para {destino} via Mailjet API")
            return True
        print(f"[Mailjet API] Envio não confirmado: {data}")
        return False
    except Exception as e:
        print(f"[Mailjet API] Erro ao enviar para {destino}: {e}")
        return False


def enviar_email(
    destino: str,
    assunto: str,
    corpo: str,
    anexos: list[str | Path] | None = None,
    html: str | None = None,
    *,
    smtp_user: str | None = None,
    smtp_pass: str | None = None,
    smtp_server: str | None = None,
    smtp_port: int | None = None,
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
) -> bool:
    # Configura remetente e headers comuns
    _login_user = smtp_user or SMTP_USER or EMAIL
    _pass = smtp_pass or SENHA
    _server = smtp_server or SMTP_SERVER
    _port = int(smtp_port or SMTP_PORT)
    _from_email = (from_email or EMAIL) if (from_email or EMAIL) else _login_user
    _from_name = from_name if from_name is not None else FROM_NAME
    _reply_to = reply_to if reply_to is not None else (REPLY_TO or _from_email)

    # Caminho via API do Mailjet (opcional)
    if USE_MAILJET_API:
        return _send_via_mailjet_api(
            destino,
            assunto,
            corpo,
            anexos=anexos,
            html=html,
            from_email=_from_email,
            from_name=_from_name,
            reply_to=_reply_to,
        )

    # SMTP (padrão)
    msg = MIMEMultipart('mixed')
    display_from = formataddr(((_from_name or '').strip(), _from_email)) if _from_name else _from_email
    msg['From'] = display_from
    msg['To'] = destino
    msg['Subject'] = assunto
    if _reply_to:
        msg['Reply-To'] = _reply_to
    if LIST_UNSUBSCRIBE:
        msg['List-Unsubscribe'] = LIST_UNSUBSCRIBE

    alternative = MIMEMultipart('alternative')
    alternative.attach(MIMEText(corpo, 'plain'))
    if html and not TEXT_ONLY:
        alternative.attach(MIMEText(html, 'html'))
    msg.attach(alternative)

    try:
        server = smtplib.SMTP(_server, _port, timeout=60)
        if DEBUG_SMTP:
            server.set_debuglevel(1)
        # Handshake + STARTTLS
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(_login_user, _pass)
        # anexos
        if anexos:
            for path in anexos:
                if not path:
                    continue
                p = Path(path)
                if not p.exists() or not p.is_file():
                    print(f"Anexo não encontrado, ignorado: {p}")
                    continue
                ctype, encoding = mimetypes.guess_type(str(p))
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                with open(p, 'rb') as f:
                    part = MIMEApplication(f.read(), _subtype=subtype)
                part.add_header('Content-Disposition', 'attachment', filename=p.name)
                msg.attach(part)
        refused = server.send_message(msg)
        server.quit()
        if refused:
            # refused contém dict: {recipient: (code, resp)}
            print(f"Envio parcialmente recusado pelo servidor: {refused}")
            return False
        print(f"E-mail enviado para {destino}")
        return True
    except Exception as e:
        print(f"Erro ao enviar para {destino}: {e}")
        return False


def enviar_em_lote(
    contatos,
    assunto: str,
    template: str,
    intervalo: int = SEND_INTERVAL,
    anexos: list[str | Path] | None = None,
    html_template: str | None = None,
    *,
    smtp_user: str | None = None,
    smtp_pass: str | None = None,
    smtp_server: str | None = None,
    smtp_port: int | None = None,
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
):
    """Itera sobre os contatos, envia e-mail com template formatado e espera intervalo."""
    for i, row in contatos.iterrows():
        nome = str(row.get("Nome", "")).strip()
        destino = str(row.get("E-mail", "")).strip()

        # validação simples de e-mail e bloqueio de placeholders
        if not _email_valido(destino):
            print(f"Pulado (e-mail inválido ou placeholder): {destino}")
            yield i, False
            continue

        corpo = template.format(nome=nome)
        sucesso = enviar_email(
            destino,
            assunto,
            corpo,
            anexos=anexos,
            html=html_template,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            from_email=from_email,
            from_name=from_name,
            reply_to=reply_to,
        )
        yield i, sucesso
        # jitter de 20% para evitar cadência fixa (mínimo 1s)
        jitter = intervalo * random.uniform(-0.2, 0.2)
        espera = max(1, intervalo + jitter)
        time.sleep(espera)


def _email_valido(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    # regex simples para e-mail
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is None:
        return False
    # evita domínios/endereços de exemplo
    lower = email.lower()
    if lower == "exemplo@dominio.com" or lower.endswith("@example.com") or lower.endswith("@test.com"):
        return False
    return True
