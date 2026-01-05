"""
Script para testar o endpoint de processamento de mídias.
Execute com: python manage.py shell < test_process_media.py
"""
import os
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

import re
from django.db.models import Q
from crm.models import WhatsappMessage

# Número para teste (use um número real do seu sistema)
number = "5581999216560"  # Ajuste para um número real

clean_number = re.sub(r'\D', '', str(number))
print(f"Número limpo: {clean_number}")

# Busca mensagens de áudio pendentes
pending_audio = WhatsappMessage.objects.filter(
    Q(numero_remetente__icontains=clean_number) | Q(numero_destinatario__icontains=clean_number),
    tipo_mensagem='audio',
    texto__in=['🎤 [Áudio]', '🎤 [Áudio não transcrito]', '[audioMessage]']
)

print(f"\nÁudios pendentes encontrados: {pending_audio.count()}")
for msg in pending_audio[:5]:
    print(f"  - ID: {msg.id}, Texto: '{msg.texto}', Tipo: '{msg.tipo_mensagem}'")

# Busca imagens pendentes
pending_images = WhatsappMessage.objects.filter(
    Q(numero_remetente__icontains=clean_number) | Q(numero_destinatario__icontains=clean_number),
    tipo_mensagem='image',
    media_base64__isnull=True
)

print(f"\nImagens pendentes encontradas: {pending_images.count()}")
for msg in pending_images[:5]:
    print(f"  - ID: {msg.id}, Texto: '{msg.texto}', Base64: {bool(msg.media_base64)}")

# Lista todas as mensagens deste número para verificar os tipos
print(f"\n--- Todas as mensagens deste número ---")
all_msgs = WhatsappMessage.objects.filter(
    Q(numero_remetente__icontains=clean_number) | Q(numero_destinatario__icontains=clean_number)
).order_by('-timestamp')[:10]

for msg in all_msgs:
    print(f"  ID: {msg.id} | Tipo: {msg.tipo_mensagem:10} | Texto: {msg.texto[:40]}...")
