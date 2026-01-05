"""
Teste manual do endpoint transcribe_audio.
Execute com: python manage.py shell < test_transcribe.py
"""
import os
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from crm.models import WhatsappMessage
from crm.services.evolution_api import EvolutionService
from crm.services.audio_transcription import transcribe_from_base64

# Busca um áudio pendente
msg = WhatsappMessage.objects.filter(
    tipo_mensagem='audio',
    texto='🎤 [Áudio]'
).first()

if not msg:
    print("Nenhum áudio pendente encontrado")
    exit()

print(f"Testando mensagem ID: {msg.id}")
print(f"De: {msg.numero_remetente}")
print(f"ID Mensagem: {msg.id_mensagem}")

# Monta a key
key = {
    'id': msg.id_mensagem,
    'remoteJid': f"{msg.numero_remetente}@s.whatsapp.net",
    'fromMe': msg.de_mim
}
print(f"Key: {key}")

# Baixa mídia
print("\nBaixando mídia...")
evolution = EvolutionService()
media_result = evolution.get_media_base64(key)

if not media_result:
    print("ERRO: Não conseguiu baixar mídia")
    exit()

print(f"✅ Mídia baixada: {len(media_result.get('base64', ''))} chars")
print(f"Mimetype: {media_result.get('mimetype')}")

# Transcreve
print("\nTranscrevendo...")
try:
    result = transcribe_from_base64(media_result['base64'], media_result.get('mimetype', ''))
    if result:
        print(f"✅ Transcrição: {result.get('text')}")
        print(f"Duração: {result.get('duration')}s")
    else:
        print("ERRO: Transcrição retornou None")
except Exception as e:
    print(f"ERRO na transcrição: {e}")
    import traceback
    traceback.print_exc()
