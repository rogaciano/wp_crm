"""
Teste de busca de mensagens da Evolution API
"""
import requests
import json
import os

# Ler config do .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
API_KEY = ""
INSTANCE = ""
API_URL = "https://evo.matutec.com.br"

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
jid = f"{formatted}@s.whatsapp.net"

print(f"\nNúmero formatado: {formatted}")
print(f"JID: {jid}")

# Buscar mensagens
url = f"{API_URL}/chat/findMessages/{INSTANCE}"
print(f"\nURL de busca: {url}")

headers = {
    'apikey': API_KEY,
    'apiKey': API_KEY,
    'Content-Type': 'application/json'
}

payload = {
    "where": {
        "key": {
            "remoteJid": jid
        }
    },
    "limit": 20
}

print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    print("\nBuscando mensagens...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        print(f"\nTipo de resposta: {type(data)}")
        
        if isinstance(data, list):
            print(f"Quantidade de mensagens: {len(data)}")
            for i, msg in enumerate(data[:5]):  # Mostra as primeiras 5
                key = msg.get('key', {})
                message = msg.get('message', {})
                text = message.get('conversation', message.get('extendedTextMessage', {}).get('text', '[sem texto]'))
                from_me = key.get('fromMe', False)
                ts = msg.get('messageTimestamp', 0)
                print(f"  [{i+1}] {'-> EU' if from_me else '<- CLIENTE'}: {text[:50]}... (ts={ts})")
        elif isinstance(data, dict):
            print(f"Resposta é dict, keys: {data.keys()}")
            if 'messages' in data:
                msgs = data['messages']
                print(f"Quantidade de mensagens: {len(msgs)}")
                for i, msg in enumerate(msgs[:5]):
                    key = msg.get('key', {})
                    message = msg.get('message', {})
                    text = message.get('conversation', message.get('extendedTextMessage', {}).get('text', '[sem texto]'))
                    from_me = key.get('fromMe', False)
                    print(f"  [{i+1}] {'-> EU' if from_me else '<- CLIENTE'}: {text[:50]}...")
            else:
                print(f"Conteúdo: {json.dumps(data, indent=2)[:500]}")
                
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        print(f"Resposta raw: {response.text[:500]}")

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
