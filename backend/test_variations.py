"""
Teste do endpoint process_pending_media com variações.
Execute com: python manage.py shell < test_variations.py
"""
import os
import re
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.db.models import Q
from crm.models import WhatsappMessage

# Número do chat (com 9)
number = "5581999216560"

clean_number = re.sub(r'\D', '', str(number))
print(f"Número original: {clean_number}")

# Gera variações
variations = set([clean_number])

base = clean_number[2:] if clean_number.startswith('55') else clean_number
variations.add(base)
variations.add('55' + base)

if len(base) == 11 and base[2] == '9':
    without_9 = base[:2] + base[3:]
    variations.add(without_9)
    variations.add('55' + without_9)
elif len(base) == 10:
    with_9 = base[:2] + '9' + base[2:]
    variations.add(with_9)
    variations.add('55' + with_9)

if len(clean_number) >= 8:
    variations.add(clean_number[-8:])

print(f"Variações geradas: {sorted(variations)}")

# Monta query
q_filter = Q()
for v in variations:
    if len(v) >= 8:
        q_filter |= Q(numero_remetente__icontains=v) | Q(numero_destinatario__icontains=v)

# Busca áudios pendentes
pending_audio = WhatsappMessage.objects.filter(
    q_filter,
    tipo_mensagem='audio',
    texto__in=['🎤 [Áudio]', '🎤 [Áudio não transcrito]', '[audioMessage]']
)

print(f"\nÁudios pendentes encontrados: {pending_audio.count()}")
for msg in pending_audio:
    print(f"  - ID: {msg.id}, De: {msg.numero_remetente}, Texto: '{msg.texto}'")

# Busca imagens pendentes
pending_images = WhatsappMessage.objects.filter(
    q_filter,
    tipo_mensagem='image',
    media_base64__isnull=True
)

print(f"\nImagens pendentes encontradas: {pending_images.count()}")
for msg in pending_images:
    print(f"  - ID: {msg.id}, De: {msg.numero_remetente}")
