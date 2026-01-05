"""
Script simples para verificar mensagens no banco de dados
Execute com: python manage.py shell < check_messages.py
"""
from crm.models import WhatsappMessage
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("ANÁLISE DE MENSAGENS WHATSAPP")
print("=" * 60)

# Total de mensagens
total = WhatsappMessage.objects.count()
print(f"\nTotal de mensagens no banco: {total}")

# Mensagens enviadas (de_mim=True)
enviadas = WhatsappMessage.objects.filter(de_mim=True).count()
print(f"Mensagens enviadas (de_mim=True): {enviadas}")

# Mensagens recebidas (de_mim=False)
recebidas = WhatsappMessage.objects.filter(de_mim=False).count()
print(f"Mensagens recebidas (de_mim=False): {recebidas}")

# Mensagens com ID local (problema)
local_msgs = WhatsappMessage.objects.filter(id_mensagem__startswith='local_')
print(f"\n⚠️  Mensagens com ID local (gerado automaticamente): {local_msgs.count()}")

if local_msgs.exists():
    print("\nÚltimas 5 mensagens com ID local:")
    for msg in local_msgs.order_by('-timestamp')[:5]:
        print(f"  [{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg.id_mensagem}")
        print(f"    Para: {msg.numero_destinatario}")
        print(f"    Texto: {msg.texto[:50]}...")
        print()

# Últimas 10 mensagens enviadas
print("\n" + "=" * 60)
print("ÚLTIMAS 10 MENSAGENS ENVIADAS")
print("=" * 60)

msgs = WhatsappMessage.objects.filter(de_mim=True).order_by('-timestamp')[:10]
for i, msg in enumerate(msgs, 1):
    print(f"\n{i}. [{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"   ID: {msg.id}")
    print(f"   id_mensagem: {msg.id_mensagem}")
    print(f"   Para: {msg.numero_destinatario}")
    print(f"   Texto: {msg.texto[:60]}...")
    if msg.lead:
        print(f"   Lead: {msg.lead.nome}")
    if msg.oportunidade:
        print(f"   Oportunidade: {msg.oportunidade.nome}")

# Mensagens das últimas 24 horas
ontem = timezone.now() - timedelta(hours=24)
recentes = WhatsappMessage.objects.filter(timestamp__gte=ontem)
print(f"\n" + "=" * 60)
print(f"MENSAGENS DAS ÚLTIMAS 24 HORAS: {recentes.count()}")
print("=" * 60)

enviadas_24h = recentes.filter(de_mim=True).count()
recebidas_24h = recentes.filter(de_mim=False).count()
print(f"Enviadas: {enviadas_24h}")
print(f"Recebidas: {recebidas_24h}")

print("\n" + "=" * 60)
print("FIM DA ANÁLISE")
print("=" * 60)
