"""
Script de diagnóstico para transcrição de áudio.
Execute com: python manage.py shell < diagnose_audio.py
"""
import os
import sys
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

print("=" * 60)
print("DIAGNÓSTICO DE TRANSCRIÇÃO DE ÁUDIO")
print("=" * 60)

# 1. Verifica faster-whisper
print("\n1️⃣ Verificando faster-whisper...")
try:
    from faster_whisper import WhisperModel
    print("   ✅ faster-whisper instalado")
except ImportError as e:
    print(f"   ❌ faster-whisper NÃO instalado: {e}")
    print("   → Execute: pip install faster-whisper")

# 2. Verifica FFmpeg
print("\n2️⃣ Verificando FFmpeg...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"   ✅ FFmpeg instalado: {version}")
    else:
        print(f"   ❌ FFmpeg não encontrado")
except FileNotFoundError:
    print("   ❌ FFmpeg NÃO instalado")
    print("   → Execute: sudo apt install ffmpeg")

# 3. Verifica configurações do Whisper
print("\n3️⃣ Verificando configurações...")
from django.conf import settings
model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
device = getattr(settings, 'WHISPER_DEVICE', 'cpu')
compute_type = getattr(settings, 'WHISPER_COMPUTE_TYPE', 'int8')
print(f"   Modelo: {model_size}")
print(f"   Device: {device}")
print(f"   Compute: {compute_type}")

# 4. Tenta carregar o modelo
print("\n4️⃣ Tentando carregar o modelo Whisper...")
try:
    from crm.services.audio_transcription import get_whisper_model
    model = get_whisper_model()
    if model:
        print("   ✅ Modelo carregado com sucesso!")
    else:
        print("   ❌ Falha ao carregar modelo")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Testa Evolution API para baixar mídia
print("\n5️⃣ Testando Evolution API (download de mídia)...")
from crm.services.evolution_api import EvolutionService
from crm.models import WhatsappMessage

# Busca uma mensagem de áudio recente
audio_msg = WhatsappMessage.objects.filter(
    tipo_mensagem='audio',
    de_mim=False
).order_by('-timestamp').first()

if audio_msg:
    print(f"   Encontrada mensagem de áudio: ID {audio_msg.id}")
    print(f"   De: {audio_msg.numero_remetente}")
    print(f"   Texto atual: {audio_msg.texto[:50]}...")
    
    # Tenta reprocessar
    print("\n   Tentando baixar mídia via Evolution API...")
    try:
        evolution = EvolutionService()
        # Simula a key da mensagem
        key = {
            'id': audio_msg.id_mensagem,
            'remoteJid': f"{audio_msg.numero_remetente}@s.whatsapp.net",
            'fromMe': audio_msg.de_mim
        }
        print(f"   Key: {key}")
        
        result = evolution.get_media_base64(key)
        if result:
            print(f"   ✅ Mídia baixada! Tamanho base64: {len(result.get('base64', ''))} chars")
            print(f"   Mimetype: {result.get('mimetype', 'N/A')}")
            
            # Tenta transcrever
            print("\n   Tentando transcrever...")
            from crm.services.audio_transcription import transcribe_from_base64
            transcription = transcribe_from_base64(result['base64'], result.get('mimetype', ''))
            if transcription:
                print(f"   ✅ Transcrição: {transcription.get('text', '')[:100]}...")
            else:
                print("   ❌ Falha na transcrição")
        else:
            print("   ❌ Falha ao baixar mídia da Evolution API")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ⚠️ Nenhuma mensagem de áudio encontrada no banco")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
