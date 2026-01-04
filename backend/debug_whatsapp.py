"""
Teste de debug para envio de mensagem WhatsApp
"""
import os
import sys
import django

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from crm.models import WhatsappMessage, Lead
from crm.services.evolution_api import EvolutionService
from django.conf import settings
import uuid

def test_send():
    print("=" * 50)
    print("TESTE DE ENVIO WHATSAPP")
    print("=" * 50)
    
    # Busca um lead com o telefone especificado
    lead = Lead.objects.filter(telefone__icontains="81999216560").first()
    print(f"Lead encontrado: {lead}")
    if lead:
        print(f"  - ID: {lead.id}")
        print(f"  - Nome: {lead.nome}")
        print(f"  - Telefone: {lead.telefone}")
    
    # Dados do teste
    number = "81999216560"
    text = f"Teste debug - {timezone.now().strftime('%H:%M:%S')}"
    lead_id = lead.id if lead else None
    
    service = EvolutionService()
    print(f"\nEvolution API Config:")
    print(f"  - URL: {service.base_url}")
    print(f"  - Instance: {service.instance}")
    print(f"  - API Key: {service.api_key[:10]}...")
    
    try:
        print(f"\nEnviando para {number}...")
        result = service.send_text(number, text)
        print(f"Resposta da API Evolution:")
        print(f"  Tipo: {type(result)}")
        print(f"  Conteúdo: {result}")
        
        # Extrai ID da mensagem
        msg_id = None
        if isinstance(result, dict):
            if 'key' in result and isinstance(result['key'], dict):
                msg_id = result['key'].get('id')
                print(f"  ID encontrado em result['key']['id']: {msg_id}")
            elif 'data' in result and isinstance(result['data'], dict):
                data_obj = result['data']
                if 'key' in data_obj and isinstance(data_obj['key'], dict):
                    msg_id = data_obj['key'].get('id')
                    print(f"  ID encontrado em result['data']['key']['id']: {msg_id}")
        
        if not msg_id:
            msg_id = f"local_{uuid.uuid4().hex[:20]}"
            print(f"  ID não encontrado, gerando local: {msg_id}")
        
        # Formata número
        formatted_number = service._format_number(number)
        print(f"  Número formatado: {formatted_number}")
        
        # Salva localmente
        print(f"\nSalvando mensagem no banco...")
        msg = WhatsappMessage.objects.create(
            id_mensagem=msg_id,
            instancia=settings.EVOLUTION_INSTANCE_ID,
            de_mim=True,
            numero_remetente=settings.EVOLUTION_INSTANCE_ID,
            numero_destinatario=formatted_number,
            texto=text,
            timestamp=timezone.now(),
            lead_id=lead_id,
            oportunidade_id=None
        )
        print(f"  Mensagem salva com sucesso!")
        print(f"  ID no banco: {msg.id}")
        print(f"  ID mensagem: {msg.id_mensagem}")
        
    except Exception as e:
        import traceback
        print(f"\nERRO: {str(e)}")
        print("\nTraceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    test_send()
