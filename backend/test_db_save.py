"""
Teste de salvamento de mensagem no banco de dados
"""
import os
import sys
import django

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from crm.models import WhatsappMessage, Lead
import uuid

print("=" * 50)
print("TESTE DE SALVAMENTO NO BANCO")
print("=" * 50)

# Config
instance_id = settings.EVOLUTION_INSTANCE_ID
print(f"EVOLUTION_INSTANCE_ID: '{instance_id}'")
print(f"Tamanho: {len(instance_id)}")

# Dados de teste
test_data = {
    'id_mensagem': f"test_{uuid.uuid4().hex[:20]}",
    'instancia': instance_id,
    'de_mim': True,
    'numero_remetente': instance_id,
    'numero_destinatario': '5581999216560',
    'texto': 'Teste salvamento direto',
    'timestamp': timezone.now(),
    'lead_id': None,
    'oportunidade_id': None
}

print(f"\nDados a serem salvos:")
for k, v in test_data.items():
    print(f"  {k}: {v} (tipo: {type(v).__name__})")

# Busca lead
lead = Lead.objects.filter(telefone__icontains="81999216560").first()
if lead:
    print(f"\nLead encontrado: {lead.id} - {lead.nome}")
    test_data['lead_id'] = lead.id

# Tenta salvar
try:
    print("\nTentando criar WhatsappMessage...")
    msg = WhatsappMessage.objects.create(**test_data)
    print(f"SUCESSO! Mensagem criada com ID: {msg.id}")
    print(f"  id_mensagem: {msg.id_mensagem}")
    print(f"  timestamp: {msg.timestamp}")
    
except Exception as e:
    import traceback
    print(f"\nERRO: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()

# Listar mensagens existentes
print("\n" + "=" * 50)
print("MENSAGENS EXISTENTES NO BANCO:")
print("=" * 50)
msgs = WhatsappMessage.objects.all()[:10]
for m in msgs:
    print(f"  [{m.id}] {m.id_mensagem[:30]}... | {m.numero_remetente} -> {m.numero_destinatario}")
