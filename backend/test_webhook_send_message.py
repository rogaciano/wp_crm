"""
Script para testar se o webhook processa corretamente eventos SEND_MESSAGE
"""
import requests
import json
import time

# URL do webhook local
WEBHOOK_URL = "http://localhost:8000/api/webhooks/whatsapp/"

# Payload simulando evento SEND_MESSAGE da Evolution API
payload = {
    "event": "send_message",
    "instance": "informsistemas",
    "data": {
        "key": {
            "remoteJid": "5581999216560@s.whatsapp.net",
            "fromMe": True,
            "id": f"TEST_SEND_{int(time.time())}"
        },
        "message": {
            "conversation": f"Teste de mensagem enviada - {time.strftime('%H:%M:%S')}"
        },
        "messageTimestamp": int(time.time())
    }
}

print("=" * 60)
print("TESTE DO WEBHOOK - EVENTO SEND_MESSAGE")
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

    try:
        result = response.json()
        print(f"Response JSON: {json.dumps(result, indent=2)}")
    except:
        print(f"Response Text: {response.text[:500]}")

    if response.status_code == 200:
        print("\n✅ WEBHOOK PROCESSOU O EVENTO SEND_MESSAGE COM SUCESSO!")
        print("Verifique o banco de dados para confirmar que a mensagem foi salva.")
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
