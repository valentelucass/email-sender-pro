from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import io
import os

# Reuso do core existente
from src.email_sender import enviar_em_lote
from src.excel_reader import ler_contatos
from src.config import (
    SEND_INTERVAL,
    DAILY_LIMIT as CONF_DAILY_LIMIT,
)

app = Flask(__name__, static_folder="web", static_url_path="/")

# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# CORS configuration for production
if os.getenv('VERCEL_ENV') == 'production':
    CORS(app, origins=['https://*.vercel.app'])
else:
    CORS(app)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/help")
def help_page():
    return send_from_directory(app.static_folder, "help.html")


# Favicon (evita 404/500 em ambientes de produção)
@app.route("/favicon.ico")
def favicon():
    try:
        return send_from_directory(app.static_folder, "favicon.ico")
    except Exception:
        return ("", 204)


# Healthcheck simples para plataformas de deploy
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/send", methods=["POST"])
def api_send():
    try:
        # Arquivo Excel
        if "file" not in request.files:
            return jsonify({"error": "Arquivo 'file' (Excel) é obrigatório"}), 400
        up = request.files["file"]
        data = up.read()
        if not data:
            return jsonify({"error": "Arquivo vazio"}), 400

        # Campos texto
        subject = request.form.get("subject", "").strip()
        text_template = request.form.get("text_template", "").strip()
        html_template = request.form.get("html_template")
        html_template = html_template if html_template and html_template.strip() else None

        # SMTP: obrigatoriamente vindas do formulário (multiusuário).
        smtp_user = (request.form.get("smtp_user") or "").strip()
        smtp_pass = (request.form.get("smtp_pass") or "").strip()
        smtp_server = (request.form.get("smtp_server") or "").strip()
        smtp_port = (request.form.get("smtp_port") or "").strip() or "587"
        from_name = (request.form.get("from_name") or "").strip()
        reply_to = (request.form.get("reply_to") or "").strip()
        from_email = (request.form.get("from_email") or smtp_user).strip()

        # Limite diário
        try:
            daily_limit = int(request.form.get("daily_limit", str(CONF_DAILY_LIMIT)))
        except Exception:
            daily_limit = CONF_DAILY_LIMIT
        daily_limit = max(0, min(100, daily_limit))

        # Validacoes básicas
        if not subject:
            return jsonify({"error": "'subject' é obrigatório"}), 400
        if not text_template:
            return jsonify({"error": "'text_template' é obrigatório"}), 400
        if not smtp_user or not smtp_pass or not smtp_server or not smtp_port:
            return jsonify({"error": "Credenciais SMTP ausentes. Informe Gmail, Senha de App, servidor e porta."}), 400

        # Ler Excel em memória
        import pandas as pd
        df = pd.read_excel(io.BytesIO(data))

        # Normalização de nomes de colunas (case-insensitive, remove pontuação simples)
        def _norm(s: str) -> str:
            return (
                str(s)
                .strip()
                .lower()
                .replace("-", "")
                .replace("_", "")
                .replace(" ", "")
            )

        colmap = {c: _norm(c) for c in df.columns}
        email_col = None
        nome_col = None
        status_col = None
        for original, normed in colmap.items():
            # qualquer coluna que contenha 'mail' será considerada email
            if "mail" in normed and email_col is None:
                email_col = original
            if normed in {"nome", "name"}:
                nome_col = original
            if normed == "status":
                status_col = original

        # Renomear para padrão se encontrado
        if email_col and email_col != "E-mail":
            df.rename(columns={email_col: "E-mail"}, inplace=True)
            email_col = "E-mail"
        if nome_col and nome_col != "Nome":
            df.rename(columns={nome_col: "Nome"}, inplace=True)
            nome_col = "Nome"
        if status_col and status_col != "Status":
            df.rename(columns={status_col: "Status"}, inplace=True)
            status_col = "Status"

        # Se Status ausente, criar
        if "Status" not in df.columns:
            df["Status"] = "Aguardando"

        # Garantir coluna de e-mail
        if "E-mail" not in df.columns:
            return jsonify({"error": "Planilha inválida: coluna de e-mail ausente. Use 'E-mail' ou 'Email'."}), 400

        # Normalizar coluna de e-mail (preencher vazios antes de converter para string)
        df["E-mail"] = df["E-mail"].fillna("")
        df["E-mail"] = df["E-mail"].astype(str).str.strip()

        # Filtrar registros elegíveis: não contatados e com e-mail preenchido
        df_pend = df[(df["Status"] != "Contatado") & (df["E-mail"] != "")].copy()
        df_envio = df_pend.head(daily_limit).copy()
        # Debug leve (contagens) — aparece no console do Flask
        try:
            print(f"[api/send] total={len(df)} pendentes={len(df_pend)} a_enviar={len(df_envio)} limite={daily_limit}")
        except Exception:
            pass

        results = []
        for i, sucesso in enviar_em_lote(
            df_envio,
            subject,
            text_template,
            intervalo=SEND_INTERVAL,
            anexos=None,
            html_template=html_template,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            smtp_server=smtp_server,
            smtp_port=int(smtp_port),
            from_email=from_email,
            from_name=from_name,
            reply_to=reply_to,
        ):
            # Captura e-mail para relatório
            email = None
            if "E-mail" in df_envio.columns:
                try:
                    email = df_envio.loc[i, "E-mail"]
                except Exception:
                    email = None
            status = "Contatado" if sucesso else "Erro"
            results.append({"index": int(i) if isinstance(i, (int, float)) else str(i), "email": email, "success": bool(sucesso), "status": status})

        summary = {
            "requested": len(df_envio),
            "sent_ok": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "limit": daily_limit,
        }

        return jsonify({"summary": summary, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Local development
    app.run(host="0.0.0.0", port=8000, debug=False)
