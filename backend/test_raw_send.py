"""
Teste mínimo de envio sem depender de todo Django framework
"""
import requests
import json

# Config Evolution
API_URL = "https://evo.matutec.com.br"
API_KEY = ""  # Pegar do .env
INSTANCE = ""  # Pegar do .env

# Ler do .env
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key == 'EVOLUTION_API_KEY':
                    API_KEY = value.strip()
                elif key == 'EVOLUTION_INSTANCE_ID':
                    INSTANCE = value.strip()
                elif key == 'EVOLUTION_API_URL':
                    API_URL = value.strip()

print(f"API URL: {API_URL}")
print(f"Instance: {INSTANCE}")
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "API Key: EMPTY!")

# Formatação de número
def format_number(number):
    clean = ''.join(filter(str.isdigit, str(number)))
    if clean.startswith('55') and len(clean) in (12, 13):
        return clean
    if 10 <= len(clean) <= 11:
        return '55' + clean
    return clean

number = "81999216560"
formatted = format_number(number)
print(f"\nNúmero formatado: {formatted}")

# Enviar mensagem
url = f"{API_URL}/message/sendText/{INSTANCE}"
print(f"\nURL de envio: {url}")

headers = {
    'apikey': API_KEY,
    'apiKey': API_KEY,
    'Content-Type': 'application/json'
}

payload = {
    "number": formatted,
    "text": "Teste debug direto",
    "delay": 1200,
    "linkPreview": True
}

print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    print("\nEnviando...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"Response JSON: {json.dumps(data, indent=2)}")
    except:
        print(f"Response Text: {response.text[:500]}")

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
