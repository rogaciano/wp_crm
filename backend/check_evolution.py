"""
Script para verificar logs de webhook na Evolution API
"""
import requests
import json
import os

# Carrega configurações
env_path = os.path.join(os.path.dirname(__file__), '.env')
config = {}
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

api_key = config.get('EVOLUTION_API_KEY', '')
instance = config.get('EVOLUTION_INSTANCE_ID', '')
api_url = config.get('EVOLUTION_API_URL', 'https://evo.matutec.com.br')

headers = {
    'apikey': api_key,
    'Content-Type': 'application/json'
}

print("=" * 60)
print("VERIFICANDO INSTÂNCIA E WEBHOOK")
print("=" * 60)

# 1. Verificar status da instância
print("\n1. Status da Instância:")
try:
    url = f"{api_url}/instance/connectionState/{instance}"
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   State: {data.get('state', data)}")
except Exception as e:
    print(f"   Erro: {e}")

# 2. Verificar configuração do webhook
print("\n2. Configuração do Webhook:")
try:
    url = f"{api_url}/webhook/find/{instance}"
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    print(f"   Status: {response.status_code}")
    if data:
        print(f"   Enabled: {data.get('enabled')}")
        print(f"   URL: {data.get('url')}")
        print(f"   Events: {data.get('events')}")
    else:
        print("   ❌ Webhook não configurado!")
except Exception as e:
    print(f"   Erro: {e}")

# 3. Tentar reconfigurar o webhook
print("\n3. Reconfigurando Webhook...")
try:
    url = f"{api_url}/webhook/set/{instance}"
    payload = {
        "url": "https://crm.sistema9.com.br/api/webhooks/whatsapp/",
        "webhook_by_events": False,
        "webhook_base64": False,
        "events": [
            "MESSAGES_UPSERT"
        ]
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Erro: {e}")

# 4. Verificar novamente
print("\n4. Verificando após reconfiguração:")
try:
    url = f"{api_url}/webhook/find/{instance}"
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    if data:
        print(f"   ✅ Enabled: {data.get('enabled')}")
        print(f"   ✅ URL: {data.get('url')}")
        print(f"   ✅ Events: {data.get('events')}")
except Exception as e:
    print(f"   Erro: {e}")

print("\n" + "=" * 60)
