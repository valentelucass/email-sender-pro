import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importa o app do Flask
from app import app as application

# Expor `app` para compatibilidade com Vercel
app = application

# Configurações adicionais para produção (não fixar SERVER_NAME no Vercel)
if os.environ.get('VERCEL_ENV') == 'production':
    application.config.update(PREFERRED_URL_SCHEME='https')
    # Configurações específicas para ambiente serverless
    application.config.update(PROPAGATE_EXCEPTIONS=True)

# Handler para Vercel serverless
from flask import request as flask_request

def handler(request, context):
    """Função handler para ambiente serverless do Vercel"""
    return application(request['headers'], request['body'])

# Execução local
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
