import requests

def test_requests_module():
    print("Testando o módulo requests...")
    try:
        response = requests.get("https://httpbin.org/get")
        print(f"Status code: {response.status_code}")
        print("Módulo requests está funcionando corretamente!")
        return True
    except Exception as e:
        print(f"Erro ao usar o módulo requests: {e}")
        return False

if __name__ == "__main__":
    test_requests_module()