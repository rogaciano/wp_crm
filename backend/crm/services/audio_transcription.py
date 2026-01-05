"""
Serviço de Transcrição de Áudio usando Faster-Whisper
"""
import os
import tempfile
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Modelo será carregado sob demanda (lazy loading)
_whisper_model = None


def get_whisper_model():
    """Carrega o modelo Whisper sob demanda (singleton)"""
    global _whisper_model
    
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            
            # Configuração do modelo via settings ou padrão
            model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
            device = getattr(settings, 'WHISPER_DEVICE', 'cpu')
            compute_type = getattr(settings, 'WHISPER_COMPUTE_TYPE', 'int8')
            
            logger.info(f"[Whisper] Carregando modelo '{model_size}' no dispositivo '{device}'...")
            _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info(f"[Whisper] Modelo carregado com sucesso!")
            
        except ImportError:
            logger.error("[Whisper] faster-whisper não está instalado. Execute: pip install faster-whisper")
            return None
        except Exception as e:
            logger.error(f"[Whisper] Erro ao carregar modelo: {str(e)}")
            return None
    
    return _whisper_model


def download_audio(url: str, headers: dict = None) -> str:
    """
    Baixa um arquivo de áudio de uma URL e retorna o caminho do arquivo temporário.
    """
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Determina a extensão do arquivo
        content_type = response.headers.get('content-type', '')
        if 'ogg' in content_type or 'opus' in content_type:
            ext = '.ogg'
        elif 'mpeg' in content_type or 'mp3' in content_type:
            ext = '.mp3'
        elif 'wav' in content_type:
            ext = '.wav'
        else:
            ext = '.ogg'  # Padrão do WhatsApp
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
            
    except Exception as e:
        logger.error(f"[Whisper] Erro ao baixar áudio: {str(e)}")
        return None


def transcribe_audio(audio_path: str, language: str = 'pt') -> dict:
    """
    Transcreve um arquivo de áudio usando Faster-Whisper.
    
    Args:
        audio_path: Caminho para o arquivo de áudio
        language: Código do idioma (pt para português)
    
    Returns:
        dict com 'text' (transcrição completa), 'segments' (lista de segmentos com timestamps)
        ou None se falhar
    """
    model = get_whisper_model()
    if model is None:
        return None
    
    try:
        logger.info(f"[Whisper] Transcrevendo áudio: {audio_path}")
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Remove silêncios
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Converte o gerador para lista e extrai o texto
        segments_list = []
        full_text = []
        
        for segment in segments:
            segments_list.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
            })
            full_text.append(segment.text.strip())
        
        transcription = ' '.join(full_text)
        
        logger.info(f"[Whisper] Transcrição concluída: {len(transcription)} caracteres")
        
        return {
            'text': transcription,
            'segments': segments_list,
            'language': info.language,
            'duration': info.duration
        }
        
    except Exception as e:
        logger.error(f"[Whisper] Erro na transcrição: {str(e)}")
        return None
    finally:
        # Limpa o arquivo temporário se existir
        if audio_path and os.path.exists(audio_path) and audio_path.startswith(tempfile.gettempdir()):
            try:
                os.remove(audio_path)
            except:
                pass


def transcribe_from_url(url: str, headers: dict = None, language: str = 'pt') -> dict:
    """
    Baixa e transcreve áudio de uma URL.
    
    Args:
        url: URL do arquivo de áudio
        headers: Headers opcionais para a requisição (ex: autenticação)
        language: Código do idioma
    
    Returns:
        dict com 'text' e 'segments' ou None se falhar
    """
    audio_path = download_audio(url, headers)
    if audio_path is None:
        return None
    
    return transcribe_audio(audio_path, language)


def transcribe_from_base64(base64_data: str, mimetype: str = '', language: str = 'pt') -> dict:
    """
    Transcreve áudio a partir de dados Base64 (formato da Evolution API).
    
    Args:
        base64_data: String Base64 do áudio
        mimetype: Tipo MIME do áudio (ex: audio/ogg; codecs=opus)
        language: Código do idioma
    
    Returns:
        dict com 'text' e 'segments' ou None se falhar
    """
    import base64
    
    try:
        # Determina a extensão do arquivo baseado no mimetype
        if 'opus' in mimetype or 'ogg' in mimetype:
            ext = '.ogg'
        elif 'mp3' in mimetype or 'mpeg' in mimetype:
            ext = '.mp3'
        elif 'wav' in mimetype:
            ext = '.wav'
        elif 'webm' in mimetype:
            ext = '.webm'
        elif 'mp4' in mimetype or 'm4a' in mimetype:
            ext = '.m4a'
        else:
            ext = '.ogg'  # Padrão do WhatsApp
        
        # Remove prefixo data:audio/... se existir
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',', 1)[-1]
        
        # Decodifica o Base64
        audio_bytes = base64.b64decode(base64_data)
        
        # Salva em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(audio_bytes)
            audio_path = tmp_file.name
        
        logger.info(f"[Whisper] Áudio Base64 salvo: {audio_path} ({len(audio_bytes)} bytes)")
        
        # Transcreve
        return transcribe_audio(audio_path, language)
        
    except Exception as e:
        logger.error(f"[Whisper] Erro ao processar áudio Base64: {str(e)}")
        return None
