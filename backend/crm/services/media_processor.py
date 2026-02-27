"""
Serviço para processamento assíncrono de mídias do WhatsApp.
Usa threading para não bloquear o webhook.
"""
import threading
import time
import logging
from django.db import connection

logger = logging.getLogger(__name__)


def process_audio_async(message_id: int, delay: float = 2.0):
    """
    Processa áudio de forma assíncrona após um delay.
    O delay permite que a mídia esteja disponível na Evolution API.
    """
    def _process():
        # Aguarda um tempo para a mídia estar disponível
        time.sleep(delay)
        
        # Fecha conexões antigas que podem ter sido herdadas
        connection.close()
        
        try:
            from crm.models import WhatsappMessage
            from crm.services.evolution_api import EvolutionService
            from crm.services.audio_transcription import transcribe_from_base64
            
            msg = WhatsappMessage.objects.get(id=message_id)
            
            # Só processa se ainda não foi transcrito
            if msg.texto and '🎤 [Áudio]' in msg.texto and 's]:' not in msg.texto:
                logger.info(f"[AsyncAudio] Processando mensagem {message_id}...")
                
                evolution = EvolutionService()
                key = {
                    'id': msg.id_mensagem,
                    'remoteJid': f"{msg.numero_remetente}@s.whatsapp.net",
                    'fromMe': msg.de_mim
                }
                
                # Tenta baixar a mídia (com retry)
                media_result = None
                for attempt in range(3):
                    media_result = evolution.get_media_base64(key)
                    if media_result and media_result.get('base64'):
                        break
                    logger.warning(f"[AsyncAudio] Tentativa {attempt + 1}/3 falhou, aguardando...")
                    time.sleep(2)
                
                if media_result and media_result.get('base64'):
                    # Salva base64 do áudio para reprodução futura
                    mimetype = media_result.get('mimetype', 'audio/ogg; codecs=opus')
                    audio_b64 = media_result['base64']
                    if not audio_b64.startswith('data:'):
                        audio_b64 = f"data:{mimetype};base64,{audio_b64}"
                    msg.media_base64 = audio_b64

                    # Transcreve
                    transcription = transcribe_from_base64(
                        media_result['base64'],
                        media_result.get('mimetype', '')
                    )
                    
                    if transcription and transcription.get('text'):
                        duration = transcription.get('duration', 0)
                        new_text = f"🎤 [Áudio {int(duration)}s]: {transcription['text']}"
                        
                        msg.texto = new_text
                        msg.save(update_fields=['texto', 'media_base64'])
                        
                        logger.info(f"[AsyncAudio] Mensagem {message_id} transcrita com sucesso!")
                    else:
                        msg.save(update_fields=['media_base64'])
                        logger.warning(f"[AsyncAudio] Transcrição retornou vazio para {message_id}, áudio salvo")
                else:
                    logger.warning(f"[AsyncAudio] Não foi possível baixar mídia para {message_id}")
                    
        except WhatsappMessage.DoesNotExist:
            logger.error(f"[AsyncAudio] Mensagem {message_id} não encontrada")
        except Exception as e:
            logger.error(f"[AsyncAudio] Erro ao processar {message_id}: {e}")
    
    # Inicia thread em background
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()
    logger.info(f"[AsyncAudio] Agendado processamento da mensagem {message_id} em {delay}s")


def process_image_async(message_id: int, delay: float = 1.0):
    """
    Processa imagem de forma assíncrona para baixar o base64.
    """
    def _process():
        time.sleep(delay)
        connection.close()
        
        try:
            from crm.models import WhatsappMessage
            from crm.services.evolution_api import EvolutionService
            
            msg = WhatsappMessage.objects.get(id=message_id)
            
            # Só processa se ainda não tem base64
            if msg.tipo_mensagem == 'image' and not msg.media_base64:
                logger.info(f"[AsyncImage] Processando imagem {message_id}...")
                
                evolution = EvolutionService()
                key = {
                    'id': msg.id_mensagem,
                    'remoteJid': f"{msg.numero_remetente}@s.whatsapp.net",
                    'fromMe': msg.de_mim
                }
                
                media_result = evolution.get_media_base64(key)
                
                if media_result and media_result.get('base64'):
                    mimetype = media_result.get('mimetype', 'image/jpeg')
                    base64_data = media_result['base64']
                    
                    if not base64_data.startswith('data:'):
                        base64_data = f"data:{mimetype};base64,{base64_data}"
                    
                    msg.media_base64 = base64_data
                    msg.save(update_fields=['media_base64'])
                    
                    logger.info(f"[AsyncImage] Imagem {message_id} salva com sucesso!")
                    
        except WhatsappMessage.DoesNotExist:
            logger.error(f"[AsyncImage] Mensagem {message_id} não encontrada")
        except Exception as e:
            logger.error(f"[AsyncImage] Erro ao processar {message_id}: {e}")
    
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()
