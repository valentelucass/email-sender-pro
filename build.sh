#!/bin/bash

# Script de build para o Vercel
echo "Iniciando build para o Vercel..."

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p .vercel/output/static/web
mkdir -p .vercel/output/functions/api

# Copiar arquivos estáticos
echo "Copiando arquivos estáticos..."
cp -r web/* .vercel/output/static/web/

# Configurar função serverless
echo "Configurando função serverless..."
cp -r api/* .vercel/output/functions/api/
cp app.py .vercel/output/functions/api/
cp -r utils .vercel/output/functions/api/

# Configurar rotas
echo "Configurando rotas..."
echo '{
  "version": 3,
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py",
      "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "X-Requested-With, Content-Type, Accept"
      }
    },
    { "handle": "filesystem" },
    { "src": "/", "dest": "/web/index.html" },
    { "src": "/(.*)", "dest": "/web/$1" }
  ]
}' > .vercel/output/config.json

echo "Build concluído com sucesso!"