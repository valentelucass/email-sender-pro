import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env na raiz do pacote email_sender/
_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")

EMAIL = os.getenv("EMAIL")
SMTP_USER = os.getenv("SMTP_USER")  # login SMTP (pode ser diferente do EMAIL/From)
SENHA = os.getenv("SENHA_APP")  # Senha/Secret (ex.: Mailjet Secret Key)
# Padrões focados em Mailjet
SMTP_SERVER = os.getenv("SMTP_SERVER", "in-v3.mailjet.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FROM_NAME = os.getenv("FROM_NAME", "")
REPLY_TO = os.getenv("REPLY_TO", EMAIL or "")
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "15"))
LIST_UNSUBSCRIBE = os.getenv("LIST_UNSUBSCRIBE", "")  # ex.: <mailto:seuemail+unsubscribe@dominio.com>
TEXT_ONLY = os.getenv("TEXT_ONLY", "false").lower() in {"1", "true", "yes"}
SUBJECT = os.getenv("SUBJECT", "Candidato a Estágio em TI – Lucas Andrade")
ATTACH_CV = os.getenv("ATTACH_CV", "true").lower() in {"1", "true", "yes"}
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "100"))
PUBLIC_MODE = os.getenv("PUBLIC_MODE", "false").lower() in {"1", "true", "yes"}
DEBUG_SMTP = os.getenv("DEBUG_SMTP", "false").lower() in {"1", "true", "yes"}

# Configuração da API HTTP do Mailjet (opcional)
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
USE_MAILJET_API = os.getenv("USE_MAILJET_API", "false").lower() in {"1", "true", "yes"}

