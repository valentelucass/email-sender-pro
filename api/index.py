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
import io
import json
from urllib.parse import parse_qs

def handler(event, context):
    """Função handler para ambiente serverless do Vercel"""
    # Extrair informações da requisição
    method = event.get('method', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    query = event.get('query', {})
    
    # Preparar o ambiente WSGI
    environ = {
        'wsgi.input': io.BytesIO(body.encode('utf-8') if isinstance(body, str) else body),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'SERVER_SOFTWARE': 'Vercel',
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query.items()]) if isinstance(query, dict) else query,
        'SERVER_NAME': 'vercel',
        'SERVER_PORT': '443',
        'CONTENT_LENGTH': str(len(body) if body else 0),
    }
    
    # Adicionar headers ao ambiente
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = 'HTTP_' + key
        environ[key] = value
    
    # Capturar a resposta
    response_body = []
    response_headers = []
    response_status = ['200 OK']
    
    def start_response(status, headers, exc_info=None):
        response_status[0] = status
        response_headers.extend(headers)
    
    # Executar a aplicação Flask
    result = application(environ, start_response)
    response_body = b''.join(result)
    
    # Extrair código de status
    status_code = int(response_status[0].split(' ')[0])
    
    # Preparar headers para resposta
    headers_dict = {}
    for header in response_headers:
        headers_dict[header[0]] = header[1]
    
    # Garantir CORS headers
    headers_dict.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Requested-With, Accept'
    })
    
    # Retornar resposta no formato esperado pela Vercel
    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': response_body.decode('utf-8')
    }

# Execução local
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
