import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importa o app do Flask
from app import app as application
# Expor também `app` para compatibilidade
app = application

# Configurações adicionais para produção (não fixar SERVER_NAME no Vercel)
if os.environ.get('VERCEL_ENV') == 'production':
    application.config.update(PREFERRED_URL_SCHEME='https')

# Execução local
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
