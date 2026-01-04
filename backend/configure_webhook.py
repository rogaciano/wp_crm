"""
Script para configurar o Webhook na Evolution API
Execute este script após fazer deploy na VPS.

Uso:
    python configure_webhook.py https://seu-crm.com
"""
import os
import sys
import requests
import json

# Carrega configurações do .env
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    config = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def configure_webhook(crm_base_url):
    config = load_env()
    
    api_key = config.get('EVOLUTION_API_KEY', '')
    instance = config.get('EVOLUTION_INSTANCE_ID', '')
    api_url = config.get('EVOLUTION_API_URL', 'https://evo.matutec.com.br')
    
    if not api_key or not instance:
        print("ERRO: EVOLUTION_API_KEY ou EVOLUTION_INSTANCE_ID não configurados no .env")
        return False
    
    # URL do webhook no CRM
    webhook_url = f"{crm_base_url.rstrip('/')}/api/webhooks/whatsapp/"
    
    print("=" * 60)
    print("CONFIGURANDO WEBHOOK NA EVOLUTION API")
    print("=" * 60)
    print(f"Evolution API: {api_url}")
    print(f"Instance: {instance}")
    print(f"Webhook URL: {webhook_url}")
    print("=" * 60)
    
    # Endpoint para configurar webhook
    url = f"{api_url}/webhook/set/{instance}"
    
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "url": webhook_url,
        "webhook_by_events": False,
        "webhook_base64": False,
        "events": [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE"
        ]
    }
    
    print(f"\nEnviando configuração para: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"\nStatus: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Resposta: {json.dumps(result, indent=2)}")
        except:
            print(f"Resposta: {response.text[:500]}")
        
        if response.status_code in [200, 201]:
            print("\n✅ WEBHOOK CONFIGURADO COM SUCESSO!")
            print(f"\nA Evolution API agora enviará eventos para:\n  {webhook_url}")
            return True
        else:
            print("\n❌ ERRO ao configurar webhook")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_current_webhook():
    """Verifica a configuração atual do webhook"""
    config = load_env()
    
    api_key = config.get('EVOLUTION_API_KEY', '')
    instance = config.get('EVOLUTION_INSTANCE_ID', '')
    api_url = config.get('EVOLUTION_API_URL', 'https://evo.matutec.com.br')
    
    url = f"{api_url}/webhook/find/{instance}"
    
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }
    
    print("\nVerificando configuração atual do webhook...")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Configuração atual:\n{json.dumps(result, indent=2)}")
        except:
            print(f"Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"ERRO: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python configure_webhook.py <URL_BASE_DO_CRM>")
        print("Exemplo: python configure_webhook.py https://crm.seudominio.com")
        print("\nOpções:")
        print("  --check   Apenas verifica a configuração atual do webhook")
        sys.exit(1)
    
    if sys.argv[1] == '--check':
        get_current_webhook()
    else:
        crm_url = sys.argv[1]
        configure_webhook(crm_url)

