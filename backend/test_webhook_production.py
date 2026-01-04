"""
Script para testar o webhook de produção
Simula uma mensagem da Evolution API e verifica se foi processada
"""
import requests
import json
import time

# URL do webhook em produção
WEBHOOK_URL = "https://crm.sistema9.com.br/api/webhooks/whatsapp/"

# Payload simulando uma mensagem recebida da Evolution API
payload = {
    "event": "messages.upsert",
    "instance": "informsistemas",
    "data": {
        "messages": [
            {
                "key": {
                    "remoteJid": "5581999216560@s.whatsapp.net",
                    "fromMe": False,
                    "id": f"WEBHOOK_TEST_{int(time.time())}"
                },
                "message": {
                    "conversation": f"Teste de webhook via script - {time.strftime('%H:%M:%S')}"
                },
                "messageTimestamp": int(time.time())
            }
        ]
    }
}

print("=" * 60)
print("TESTE DO WEBHOOK DE PRODUÇÃO")
print("=" * 60)
print(f"URL: {WEBHOOK_URL}")
print(f"Payload:\n{json.dumps(payload, indent=2)}")
print("=" * 60)

try:
    print("\nEnviando requisição...")
    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        result = response.json()
        print(f"Response JSON: {json.dumps(result, indent=2)}")
    except:
        print(f"Response Text: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ WEBHOOK RESPONDEU COM SUCESSO!")
        print("A mensagem deveria ter sido salva no banco de dados.")
    else:
        print(f"\n❌ WEBHOOK RETORNOU ERRO {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ ERRO DE CONEXÃO: O servidor não está acessível")
    print(f"Detalhes: {e}")
except requests.exceptions.Timeout:
    print(f"\n❌ TIMEOUT: O servidor demorou muito para responder")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
