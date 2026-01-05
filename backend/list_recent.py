"""
Script para listar mensagens recentes e verificar tipos.
Execute com: python manage.py shell < list_recent.py
"""
import os
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from crm.models import WhatsappMessage

print("=== ÚLTIMAS 15 MENSAGENS ===\n")
msgs = WhatsappMessage.objects.all().order_by('-timestamp')[:15]

for msg in msgs:
    remetente = msg.numero_remetente[-8:] if msg.numero_remetente else 'N/A'
    texto = msg.texto[:50] if msg.texto else '[vazio]'
    print(f"ID: {msg.id:3} | Tipo: {msg.tipo_mensagem:8} | De: ...{remetente} | Texto: {texto}")
