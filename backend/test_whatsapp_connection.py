import os
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from crm.services.evolution_api import EvolutionService

def test_evolution_connection():
    service = EvolutionService()
    print("--- Testando Conexão Evolution API ---")
    print(f"URL: {service.base_url}")
    print(f"Instância: {service.instance}")
    
    # 1. Testar Status da Instância
    status_url = f"{service.base_url}/instance/connectionState/{service.instance}"
    try:
        response = requests.get(status_url, headers=service.headers)
        print(f"\nStatus da Instância: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Erro ao buscar status: {str(e)}")

    # 2. Listar Chats (para ver se puxa dados)
    chats_url = f"{service.base_url}/chat/findChats/{service.instance}"
    try:
        response = requests.post(chats_url, json={}, headers=service.headers)
        print(f"\nBusca de Chats: {response.status_code}")
        data = response.json()
        if isinstance(data, list):
            print(f"Total de chats encontrados: {len(data)}")
        else:
            print(data)
    except Exception as e:
        print(f"Erro ao buscar chats: {str(e)}")

if __name__ == "__main__":
    test_evolution_connection()
