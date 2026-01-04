"""
Script completo para testar o fluxo de envio e recebimento de mensagens via webhook
"""
import os
import sys
import django
import time

# Configura Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.conf import settings
from crm.models import WhatsappMessage, Lead
from crm.services.evolution_api import EvolutionService
import requests
import json

def test_send_message():
    """Testa o envio de mensagem e verificação no banco"""
    print("\n" + "="*60)
    print("TESTE 1: ENVIO DE MENSAGEM VIA API")
    print("="*60)

    # Busca um lead para teste
    lead = Lead.objects.first()
    if not lead or not lead.telefone:
        print("❌ Nenhum lead com telefone encontrado para teste")
        return None

    print(f"Lead selecionado: {lead.nome} - {lead.telefone}")

    # Conta mensagens atuais
    count_before = WhatsappMessage.objects.count()
    print(f"Mensagens no banco antes: {count_before}")

    # Envia mensagem
    service = EvolutionService()
    text = f"Teste automático - {time.strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        print(f"\nEnviando mensagem para {lead.telefone}...")
        result = service.send_text(lead.telefone, text)
        print(f"Resposta da Evolution API:")
        print(json.dumps(result, indent=2))

        # Extrai ID
        msg_id = None
        if isinstance(result, dict):
            if 'key' in result and isinstance(result['key'], dict):
                msg_id = result['key'].get('id')
            elif 'data' in result and isinstance(result['data'], dict):
                data_obj = result['data']
                if 'key' in data_obj and isinstance(data_obj['key'], dict):
                    msg_id = data_obj['key'].get('id')

        print(f"\nID extraído da resposta: {msg_id or 'Não encontrado'}")

        # Aguarda um pouco para o banco processar
        time.sleep(1)

        # Verifica se foi salvo
        count_after = WhatsappMessage.objects.count()
        print(f"Mensagens no banco depois: {count_after}")
        print(f"Novas mensagens: {count_after - count_before}")

        # Busca a mensagem salva
        if msg_id:
            msg = WhatsappMessage.objects.filter(id_mensagem=msg_id).first()
            if msg:
                print(f"\n✅ Mensagem encontrada no banco!")
                print(f"   ID: {msg.id}")
                print(f"   id_mensagem: {msg.id_mensagem}")
                print(f"   de_mim: {msg.de_mim}")
                print(f"   texto: {msg.texto}")
                print(f"   lead: {msg.lead.nome if msg.lead else 'Nenhum'}")
                return msg
            else:
                print(f"\n❌ Mensagem com id_mensagem={msg_id} NÃO encontrada")
        else:
            # Tenta buscar pela última mensagem
            last_msg = WhatsappMessage.objects.filter(de_mim=True).order_by('-timestamp').first()
            if last_msg:
                print(f"\n⚠️  Última mensagem enviada:")
                print(f"   ID: {last_msg.id}")
                print(f"   id_mensagem: {last_msg.id_mensagem}")
                print(f"   texto: {last_msg.texto}")
                return last_msg

        return None

    except Exception as e:
        print(f"\n❌ ERRO ao enviar mensagem: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_webhook_simulation():
    """Simula um webhook SEND_MESSAGE"""
    print("\n" + "="*60)
    print("TESTE 2: SIMULAÇÃO DE WEBHOOK SEND_MESSAGE")
    print("="*60)

    webhook_url = "http://localhost:8000/api/webhooks/whatsapp/"

    payload = {
        "event": "send_message",
        "instance": settings.EVOLUTION_INSTANCE_ID,
        "data": {
            "key": {
                "remoteJid": "5581999216560@s.whatsapp.net",
                "fromMe": True,
                "id": f"WEBHOOK_SIM_{int(time.time())}"
            },
            "message": {
                "conversation": f"Teste de webhook - {time.strftime('%H:%M:%S')}"
            },
            "messageTimestamp": int(time.time())
        }
    }

    print(f"URL: {webhook_url}")
    print(f"Payload:\n{json.dumps(payload, indent=2)}")

    try:
        print("\nEnviando requisição ao webhook...")
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Webhook respondeu OK")

            # Verifica se foi salvo
            msg_id = payload['data']['key']['id']
            time.sleep(0.5)
            msg = WhatsappMessage.objects.filter(id_mensagem=msg_id).first()
            if msg:
                print(f"✅ Mensagem salva pelo webhook!")
                print(f"   ID: {msg.id}")
                print(f"   id_mensagem: {msg.id_mensagem}")
                print(f"   de_mim: {msg.de_mim}")
            else:
                print(f"❌ Mensagem NÃO foi salva")
        else:
            print(f"❌ Webhook retornou erro {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Servidor Django não está rodando em localhost:8000")
        print("   Inicie com: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

def test_message_listing():
    """Testa a listagem de mensagens"""
    print("\n" + "="*60)
    print("TESTE 3: LISTAGEM DE MENSAGENS")
    print("="*60)

    # Últimas 5 mensagens enviadas
    msgs = WhatsappMessage.objects.filter(de_mim=True).order_by('-timestamp')[:5]

    print(f"\nÚltimas {len(msgs)} mensagens enviadas (de_mim=True):")
    for i, msg in enumerate(msgs, 1):
        print(f"\n{i}. ID: {msg.id}")
        print(f"   id_mensagem: {msg.id_mensagem}")
        print(f"   número: {msg.numero_destinatario}")
        print(f"   texto: {msg.texto[:50]}...")
        print(f"   timestamp: {msg.timestamp}")
        print(f"   lead: {msg.lead.nome if msg.lead else 'Nenhum'}")

    # Verifica se há mensagens com ID local
    local_msgs = WhatsappMessage.objects.filter(id_mensagem__startswith='local_')
    print(f"\n⚠️  Mensagens com ID local (gerado automaticamente): {local_msgs.count()}")
    if local_msgs.exists():
        print("   Isso indica que a Evolution API não retornou o ID da mensagem.")
        for msg in local_msgs[:3]:
            print(f"   - {msg.id_mensagem}: {msg.texto[:40]}...")

if __name__ == "__main__":
    print("TESTE COMPLETO DO FLUXO DE MENSAGENS WHATSAPP")
    print("="*60)

    # Teste 1: Envio real via Evolution API
    # test_send_message()

    # Teste 2: Simulação de webhook
    # Descomente se o servidor Django estiver rodando em localhost
    # test_webhook_simulation()

    # Teste 3: Listagem de mensagens
    test_message_listing()

    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)
