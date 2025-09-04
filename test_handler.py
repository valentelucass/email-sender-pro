#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o handler da função serverless da Vercel localmente.
Este script simula uma requisição para o handler da função serverless e exibe a resposta.
"""

import json
import sys
from api.index import handler

# Simular uma requisição para o endpoint /api/health
test_request = {
    'method': 'GET',
    'path': '/api/health',
    'headers': {
        'host': 'localhost',
        'user-agent': 'Mozilla/5.0',
        'accept': 'application/json',
    },
    'body': '',
    'query': {}
}

# Chamar o handler com a requisição simulada
print("Testando handler com requisição para /api/health...")
try:
    response = handler(test_request, {})
    print("\nResposta do handler:")
    print(f"Status Code: {response.get('statusCode')}")
    print("Headers:")
    for key, value in response.get('headers', {}).items():
        print(f"  {key}: {value}")
    print("\nBody:")
    print(response.get('body'))
    print("\nTeste concluído com sucesso!")
except Exception as e:
    print(f"\nErro ao testar o handler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)