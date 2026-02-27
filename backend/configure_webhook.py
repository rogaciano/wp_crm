"""
Script para configurar o Webhook na Evolution API
Execute este script após fazer deploy na VPS.

Uso:
    python configure_webhook.py <URL_BASE_DO_CRM>                   # Configura TODOS os canais do banco
    python configure_webhook.py <URL_BASE_DO_CRM> --instance NOME   # Configura uma instância específica
    python configure_webhook.py --check                              # Verifica webhooks de todos os canais
    python configure_webhook.py --check --instance NOME              # Verifica webhook de uma instância
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


def get_instances_from_db():
    """Busca instâncias Evolution dos Canais cadastrados no banco de dados"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    django.setup()
    
    from crm.models import Canal
    
    canais = Canal.objects.filter(
        evolution_instance_name__isnull=False
    ).exclude(evolution_instance_name='').values(
        'id', 'nome', 'evolution_instance_name', 'evolution_token'
    )
    
    instances = []
    for canal in canais:
        instances.append({
            'canal_id': canal['id'],
            'canal_nome': canal['nome'],
            'instance_name': canal['evolution_instance_name'],
            'instance_token': canal['evolution_token'] or '',
        })
    
    return instances


def configure_webhook_for_instance(instance_name, api_url, api_key, webhook_url, instance_token=None):
    """Configura webhook para uma instância específica"""
    url = f"{api_url}/webhook/set/{instance_name}"
    
    # Usa token da instância se disponível, senão usa global key
    auth_key = instance_token if instance_token else api_key
    headers = {
        'apikey': auth_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "url": webhook_url,
        "webhook_by_events": False,
        "webhook_base64": True,
        "events": [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE"
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        try:
            result = response.json()
        except:
            result = response.text[:500]
        
        if response.status_code in [200, 201]:
            return True, result
        else:
            return False, result
            
    except Exception as e:
        return False, str(e)


def configure_webhook(crm_base_url, specific_instance=None):
    config = load_env()
    api_key = config.get('EVOLUTION_API_KEY', '')
    api_url = config.get('EVOLUTION_API_URL', 'https://evo.matutec.com.br')
    
    if not api_key:
        print("ERRO: EVOLUTION_API_KEY não configurada no .env")
        return False
    
    webhook_url = f"{crm_base_url.rstrip('/')}/api/webhooks/whatsapp/"
    
    # Busca instâncias do banco de dados
    instances = get_instances_from_db()
    
    if not instances:
        print("ERRO: Nenhum canal com Evolution API configurado encontrado no banco de dados.")
        return False
    
    # Filtra por instância específica se fornecida
    if specific_instance:
        instances = [i for i in instances if i['instance_name'] == specific_instance]
        if not instances:
            print(f"ERRO: Instância '{specific_instance}' não encontrada nos canais do banco.")
            print("\nInstâncias disponíveis:")
            for inst in get_instances_from_db():
                print(f"  -> {inst['instance_name']} (Canal: {inst['canal_nome']})")
            return False
    
    print("=" * 60)
    print("CONFIGURANDO WEBHOOKS NA EVOLUTION API")
    print("=" * 60)
    print(f"Evolution API: {api_url}")
    print(f"Webhook URL:   {webhook_url}")
    print(f"Instâncias:    {len(instances)}")
    print("=" * 60)
    
    success_count = 0
    for inst in instances:
        print(f"\n📡 {inst['instance_name']} (Canal: {inst['canal_nome']})")
        
        ok, result = configure_webhook_for_instance(
            inst['instance_name'], api_url, api_key, webhook_url, inst['instance_token']
        )
        
        if ok:
            print(f"   ✅ Webhook configurado com sucesso! (webhook_base64=true)")
            success_count += 1
        else:
            print(f"   ❌ ERRO: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")
    
    print(f"\n{'=' * 60}")
    print(f"Resultado: {success_count}/{len(instances)} webhooks configurados")
    print(f"{'=' * 60}")
    
    return success_count == len(instances)


def get_current_webhook(specific_instance=None):
    """Verifica a configuração atual dos webhooks"""
    config = load_env()
    api_key = config.get('EVOLUTION_API_KEY', '')
    api_url = config.get('EVOLUTION_API_URL', 'https://evo.matutec.com.br')
    
    instances = get_instances_from_db()
    
    if specific_instance:
        instances = [i for i in instances if i['instance_name'] == specific_instance]
    
    if not instances:
        print("Nenhuma instância encontrada.")
        return
    
    print("\nVerificando configuração dos webhooks...")
    print("=" * 60)
    
    for inst in instances:
        auth_key = inst['instance_token'] if inst['instance_token'] else api_key
        url = f"{api_url}/webhook/find/{inst['instance_name']}"
        headers = {'apikey': auth_key, 'Content-Type': 'application/json'}
        
        print(f"\n📡 {inst['instance_name']} (Canal: {inst['canal_nome']})")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            try:
                result = response.json()
                base64_status = result.get('webhook_base64', result.get('webhookBase64', '?'))
                wh_url = result.get('url', '?')
                print(f"   URL: {wh_url}")
                print(f"   webhook_base64: {base64_status}")
            except:
                print(f"   Resposta: {response.text[:300]}")
        except Exception as e:
            print(f"   ERRO: {e}")


if __name__ == "__main__":
    # Parse argumentos
    args = sys.argv[1:]
    specific_instance = None
    
    if '--instance' in args:
        idx = args.index('--instance')
        if idx + 1 < len(args):
            specific_instance = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            print("ERRO: --instance requer um nome de instância")
            sys.exit(1)
    
    if not args:
        print("Uso: python configure_webhook.py <URL_BASE_DO_CRM> [--instance NOME]")
        print("     python configure_webhook.py --check [--instance NOME]")
        print("\nExemplo:")
        print("  python configure_webhook.py https://crm.sistema9.com.br")
        print("  python configure_webhook.py https://crm.sistema9.com.br --instance canal_pernambuco")
        print("  python configure_webhook.py --check")
        sys.exit(1)
    
    if args[0] == '--check':
        get_current_webhook(specific_instance)
    else:
        crm_url = args[0]
        configure_webhook(crm_url, specific_instance)

