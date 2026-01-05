"""
Script para reprocessar áudios não transcritos.
Execute com: python manage.py shell < reprocess_audio.py
"""
import os
import django

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from crm.models import WhatsappMessage
from crm.services.evolution_api import EvolutionService
from crm.services.audio_transcription import transcribe_from_base64

print("=" * 60)
print("REPROCESSAMENTO DE ÁUDIOS NÃO TRANSCRITOS")
print("=" * 60)

# Busca áudios que não foram transcritos
audio_msgs = WhatsappMessage.objects.filter(
    tipo_mensagem='audio',
    texto__in=['🎤 [Áudio]', '🎤 [Áudio não transcrito]', '🎤 [Áudio - erro na transcrição]', '[audioMessage]']
).order_by('-timestamp')

print(f"\n📋 Encontrados {audio_msgs.count()} áudios para reprocessar\n")

evolution = EvolutionService()
success_count = 0
error_count = 0

for msg in audio_msgs:
    print(f"🔄 Processando ID {msg.id} de {msg.numero_remetente}...")
    
    try:
        # Monta a key da mensagem
        key = {
            'id': msg.id_mensagem,
            'remoteJid': f"{msg.numero_remetente}@s.whatsapp.net",
            'fromMe': msg.de_mim
        }
        
        # Baixa a mídia
        result = evolution.get_media_base64(key)
        
        if result and result.get('base64'):
            # Transcreve
            transcription = transcribe_from_base64(
                result['base64'], 
                result.get('mimetype', '')
            )
            
            if transcription and transcription.get('text'):
                duration = transcription.get('duration', 0)
                new_text = f"🎤 [Áudio {int(duration)}s]: {transcription['text']}"
                
                msg.texto = new_text
                msg.save(update_fields=['texto'])
                
                print(f"   ✅ Transcrito: {transcription['text'][:50]}...")
                success_count += 1
            else:
                print(f"   ❌ Falha na transcrição (sem texto)")
                error_count += 1
        else:
            print(f"   ❌ Falha ao baixar mídia")
            error_count += 1
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        error_count += 1

print("\n" + "=" * 60)
print(f"✅ {success_count} áudios transcritos com sucesso")
print(f"❌ {error_count} falhas")
print("=" * 60)
