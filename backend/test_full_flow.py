"""
Teste completo de fluxo de envio WhatsApp
"""
import os
import sys

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from django.conf import settings
from crm.models import WhatsappMessage, Lead
from crm.services.evolution_api import EvolutionService
import uuid
import json

print("=" * 60)
print("TESTE COMPLETO DE ENVIO WHATSAPP")
print("=" * 60)

# 1. Verificar configurações
print("\n[1] CONFIGURAÇÕES:")
print(f"  EVOLUTION_API_URL: {settings.EVOLUTION_API_URL}")
print(f"  EVOLUTION_INSTANCE_ID: {settings.EVOLUTION_INSTANCE_ID}")
print(f"  EVOLUTION_API_KEY: {settings.EVOLUTION_API_KEY[:10]}..." if settings.EVOLUTION_API_KEY else "  EVOLUTION_API_KEY: VAZIO!")

# 2. Buscar lead
print("\n[2] BUSCANDO LEAD:")
lead = Lead.objects.filter(telefone__icontains="81999216560").first()
if lead:
    print(f"  Encontrado: ID={lead.id}, Nome={lead.nome}, Tel={lead.telefone}")
else:
    print("  NAO ENCONTRADO!")

# 3. Testar envio
print("\n[3] TESTANDO ENVIO:")
service = EvolutionService()
number = "81999216560"
text = f"Teste completo {timezone.now().strftime('%H:%M:%S')}"

try:
    result = service.send_text(number, text)
    print(f"  Enviado com sucesso!")
    print(f"  Resposta: {json.dumps(result, indent=4)}")
    
    # 4. Extrair ID
    print("\n[4] EXTRAINDO ID DA MENSAGEM:")
    msg_id = None
    if isinstance(result, dict):
        if 'key' in result and isinstance(result['key'], dict):
            msg_id = result['key'].get('id')
            print(f"  ID encontrado em result['key']['id']: {msg_id}")
        elif 'data' in result:
            data_obj = result['data']
            if isinstance(data_obj, dict) and 'key' in data_obj:
                msg_id = data_obj['key'].get('id')
                print(f"  ID encontrado em result['data']['key']['id']: {msg_id}")
    
    if not msg_id:
        msg_id = f"local_{uuid.uuid4().hex[:20]}"
        print(f"  Usando ID local gerado: {msg_id}")
    
    # 5. Formatar número
    print("\n[5] FORMATANDO NÚMERO:")
    formatted = service._format_number(number)
    print(f"  Original: {number}")
    print(f"  Formatado: {formatted}")
    
    # 6. Criar mensagem no banco
    print("\n[6] SALVANDO NO BANCO:")
    lead_id = lead.id if lead else None
    print(f"  lead_id a ser usado: {lead_id}")
    
    msg = WhatsappMessage.objects.create(
        id_mensagem=msg_id,
        instancia=settings.EVOLUTION_INSTANCE_ID,
        de_mim=True,
        numero_remetente=settings.EVOLUTION_INSTANCE_ID,
        numero_destinatario=formatted,
        texto=text,
        timestamp=timezone.now(),
        lead_id=lead_id,
        oportunidade_id=None
    )
    print(f"  SUCESSO! Mensagem criada: ID={msg.id}, id_mensagem={msg.id_mensagem}")
    
except Exception as e:
    import traceback
    print(f"\n  ERRO: {e}")
    print("\n  Traceback:")
    traceback.print_exc()

# 7. Listar mensagens
print("\n[7] MENSAGENS NO BANCO:")
for m in WhatsappMessage.objects.all().order_by('-id')[:5]:
    print(f"  [{m.id}] {m.id_mensagem[:25]}... de_mim={m.de_mim} lead_id={m.lead_id}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
