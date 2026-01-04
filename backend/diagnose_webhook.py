"""
Script de diagnóstico do Webhook - Execute na VPS
Verifica se mensagens estão sendo salvas corretamente
"""
import os
import sys

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from crm.models import WhatsappMessage

print("=" * 60)
print("DIAGNÓSTICO DO WEBHOOK")
print("=" * 60)

# Lista as últimas mensagens
print("\n📬 ÚLTIMAS 10 MENSAGENS NO BANCO:")
print("-" * 60)

messages = WhatsappMessage.objects.all().order_by('-timestamp')[:10]

if not messages:
    print("❌ Nenhuma mensagem encontrada no banco de dados!")
else:
    for msg in messages:
        emoji = "📤" if msg.de_mim else "📥"
        print(f"{emoji} [{msg.timestamp.strftime('%d/%m %H:%M')}] ID: {msg.id_mensagem[:20]}...")
        print(f"   De: {msg.numero_remetente} → Para: {msg.numero_destinatario}")
        print(f"   Texto: {msg.texto[:50] if msg.texto else '[vazio]'}...")
        print(f"   Lead: {msg.lead_id}, Oportunidade: {msg.oportunidade_id}")
        print()

# Estatísticas
print("-" * 60)
print("\n📊 ESTATÍSTICAS:")
total = WhatsappMessage.objects.count()
enviadas = WhatsappMessage.objects.filter(de_mim=True).count()
recebidas = WhatsappMessage.objects.filter(de_mim=False).count()

print(f"   Total de mensagens: {total}")
print(f"   Enviadas (de_mim=True): {enviadas}")
print(f"   Recebidas (de_mim=False): {recebidas}")

# Verifica se houve mensagens nas últimas horas
from datetime import timedelta
ultima_hora = timezone.now() - timedelta(hours=1)
recentes = WhatsappMessage.objects.filter(timestamp__gte=ultima_hora).count()
print(f"   Mensagens na última hora: {recentes}")

print("\n" + "=" * 60)
print("Para testar o webhook, envie uma mensagem pelo celular e veja se aparece aqui.")
print("=" * 60)
