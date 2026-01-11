import requests
import json
import logging
from django.conf import settings
from datetime import datetime
from ..models import WhatsappMessage, Lead, Oportunidade
from django.db.models import Q

logger = logging.getLogger(__name__)

class EvolutionService:
    """
    Serviço para interagir com a Evolution API.
    
    Existem dois modos de uso:
    1. Global API Key (AUTHENTICATION_API_KEY): Para criar/deletar instâncias
    2. Instance Token: Para operações em uma instância específica (status, qrcode, etc)
    """
    
    def __init__(self, instance_name=None, instance_token=None):
        """
        Inicializa o serviço Evolution API.
        
        Args:
            instance_name: Nome da instância para operações específicas
            instance_token: Token da instância. Se None, usa a Global API Key
        """
        self.global_api_key = settings.EVOLUTION_API_KEY.strip()
        self.base_url = settings.EVOLUTION_API_URL.strip().rstrip('/')
        self.instance = instance_name.strip() if instance_name else settings.EVOLUTION_INSTANCE_ID.strip()
        
        # Se tiver instance_token, usa ele; senão usa a global key
        self.api_key = instance_token.strip() if instance_token else self.global_api_key
        self.headers = {
            'apikey': self.api_key,
            'apiKey': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _get_global_headers(self):
        """Retorna headers com a Global API Key (para criar/deletar instâncias)"""
        return {
            'apikey': self.global_api_key,
            'apiKey': self.global_api_key,
            'Content-Type': 'application/json'
        }

    def create_instance(self, instance_name, webhook_url=None):
        """
        Cria uma nova instância no Evolution API usando a Global API Key.
        
        Args:
            instance_name: Nome único da instância (ex: 'canal_brasilia')
            webhook_url: URL do webhook para receber eventos (opcional)
        
        Returns:
            dict com success, instance_name, token (apikey da instância), qrcode e dados
        """
        url = f"{self.base_url}/instance/create"
        
        payload = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        # Adiciona webhook se fornecido
        if webhook_url:
            payload["webhook"] = {
                "url": webhook_url,
                "webhookByEvents": True,
                "webhookBase64": True,
                "events": [
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE", 
                    "CONNECTION_UPDATE",
                    "QRCODE_UPDATED"
                ]
            }
        
        try:
            logger.info(f"[Evolution] Criando instância: {instance_name}")
            logger.info(f"[Evolution] URL: {url}")
            logger.info(f"[Evolution] API Key (primeiros 8 chars): {self.global_api_key[:8]}...")
            # Usa Global API Key para criar
            response = requests.post(url, json=payload, headers=self._get_global_headers(), timeout=30)
            logger.info(f"[Evolution] Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
            # Extrai o token/apikey retornado (pode estar em diferentes lugares)
            instance_token = None
            qr_code = None
            qr_base64 = None
            
            # A resposta pode variar, vamos tentar diferentes formatos
            if isinstance(data, dict):
                # Formato 1: {"instance": {...}, "hash": "...", "qrcode": {...}}
                instance_data = data.get('instance', data)
                instance_token = data.get('hash') or instance_data.get('token') or instance_data.get('apikey')
                
                qr_data = data.get('qrcode', {})
                if isinstance(qr_data, dict):
                    qr_code = qr_data.get('code')
                    qr_base64 = qr_data.get('base64')
                elif isinstance(qr_data, str):
                    qr_base64 = qr_data
            
            logger.info(f"[Evolution] Instância criada: {instance_name}, token: {'sim' if instance_token else 'não'}")
            
            return {
                'success': True,
                'instance_name': instance_name,
                'token': instance_token,
                'qr_code': qr_code,
                'qr_base64': qr_base64,
                'raw_data': data
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            try:
                error_data = e.response.json() if e.response else {}
                error_msg = error_data.get('message', str(e))
            except:
                pass
            logger.error(f"[Evolution] Erro ao criar instância: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    def delete_instance(self):
        """Deleta a instância atual usando Global API Key"""
        url = f"{self.base_url}/instance/delete/{self.instance}"
        
        try:
            response = requests.delete(url, headers=self._get_global_headers(), timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'message': f'Instância {self.instance} deletada'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"[Evolution] Erro ao deletar instância: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_number(self, number):
        """Remove caracteres não numéricos e garante formato DDI(55) + DDD + Numero"""
        if not number:
            return None
        
        # Converte para string e remove tudo que não é dígito
        clean_number = ''.join(filter(str.isdigit, str(number)))
        
        # Se o número começa com 55 e tem 12 ou 13 dígitos, já está com DDI
        if clean_number.startswith('55') and (len(clean_number) == 12 or len(clean_number) == 13):
            return clean_number

        # Se o número tem 10 ou 11 dígitos, adicionamos o 55
        if 10 <= len(clean_number) <= 11:
            return '55' + clean_number
            
        return clean_number

    # ==================== MÉTODOS DE CONEXÃO ====================

    def get_connection_status(self):
        """Verifica o status da conexão da instância"""
        url = f"{self.base_url}/instance/connectionState/{self.instance}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # A resposta pode variar, mas geralmente tem 'state' ou 'instance.state'
            state = data.get('state') or data.get('instance', {}).get('state', 'unknown')
            
            return {
                'connected': state == 'open',
                'state': state,
                'instance': self.instance,
                'raw': data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar status da conexão: {str(e)}")
            return {
                'connected': False,
                'state': 'error',
                'error': str(e),
                'instance': self.instance
            }

    def get_qr_code(self):
        """Obtém o QR Code para conectar o WhatsApp"""
        url = f"{self.base_url}/instance/connect/{self.instance}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # A resposta pode ter o QR code em diferentes formatos
            qr_code = None
            qr_base64 = None
            
            if 'qrcode' in data:
                qr_data = data['qrcode']
                if isinstance(qr_data, dict):
                    qr_code = qr_data.get('code') or qr_data.get('qrcode')
                    qr_base64 = qr_data.get('base64')
                else:
                    qr_code = qr_data
            elif 'base64' in data:
                qr_base64 = data['base64']
            elif 'code' in data:
                qr_code = data['code']
            
            return {
                'success': True,
                'qr_code': qr_code,
                'qr_base64': qr_base64,
                'raw': data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter QR Code: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def disconnect(self):
        """Desconecta a instância do WhatsApp"""
        url = f"{self.base_url}/instance/logout/{self.instance}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'message': 'Desconectado com sucesso'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao desconectar: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def restart_instance(self):
        """Reinicia a instância"""
        url = f"{self.base_url}/instance/restart/{self.instance}"
        
        try:
            response = requests.put(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'message': 'Instância reiniciada'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao reiniciar instância: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_instance_info(self):
        """Obtém informações da instância conectada (número, nome, etc.)"""
        url = f"{self.base_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Busca a instância específica
            instances = data if isinstance(data, list) else data.get('instances', [])
            
            for inst in instances:
                inst_name = inst.get('instance', {}).get('instanceName') or inst.get('name')
                if inst_name == self.instance:
                    return {
                        'success': True,
                        'instance': inst
                    }
            
            return {
                'success': False,
                'error': 'Instância não encontrada'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter info da instância: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== MÉTODOS DE MENSAGEM ====================

    def send_text(self, number, text):
        """Envia mensagem de texto via Evolution API"""
        formatted_number = self._format_number(number)
        url = f"{self.base_url}/message/sendText/{self.instance}"
        
        payload = {
            "number": formatted_number,
            "text": text,
            "delay": 1200,
            "linkPreview": True
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return data
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {number}: {str(e)}")
            raise e

    def send_media(self, number, media_base64, media_type='image', filename='image.jpg', caption=''):
        """
        Envia mídia (imagem, documento, etc) via Evolution API.
        
        Args:
            number: Número do destinatário
            media_base64: Arquivo em formato Base64
            media_type: Tipo de mídia ('image', 'document', 'video', 'audio')
            filename: Nome do arquivo
            caption: Legenda/texto opcional
            
        Returns:
            dict com resposta da API
        """
        formatted_number = self._format_number(number)
        url = f"{self.base_url}/message/sendMedia/{self.instance}"
        
        payload = {
            "number": formatted_number,
            "mediatype": media_type,
            "media": media_base64,
            "fileName": filename,
            "caption": caption,
            "delay": 1200
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return data
        except Exception as e:
            logger.error(f"Erro ao enviar mídia para {number}: {str(e)}")
            raise e

    def find_messages(self, number, limit=50):
        """Busca histórico de mensagens de um número"""
        formatted_number = self._format_number(number)
        url = f"{self.base_url}/chat/findMessages/{self.instance}"
        
        # O JID do WhatsApp geralmente é numero@s.whatsapp.net
        jid = f"{formatted_number}@s.whatsapp.net"
        
        payload = {
            "where": {
                "key": {
                    "remoteJid": jid
                }
            },
            "limit": limit
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens para {number}: {str(e)}")
            return []

    def get_media_base64(self, message_key: dict):
        """
        Obtém a mídia de uma mensagem em formato Base64.
        
        Args:
            message_key: O objeto 'key' da mensagem do webhook, contendo:
                - id: ID da mensagem
                - remoteJid: JID do remetente
                - fromMe: Se foi enviada por nós
        
        Returns:
            dict com 'base64' e 'mimetype' ou None se falhar
        """
        url = f"{self.base_url}/chat/getBase64FromMediaMessage/{self.instance}"
        
        payload = {
            "message": {
                "key": message_key
            },
            "convertToMp4": False
        }
        
        try:
            logger.info(f"[Evolution] Baixando mídia: {message_key.get('id', '')[:20]}...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            base64_data = data.get('base64')
            mimetype = data.get('mimetype', '')
            
            if base64_data:
                logger.info(f"[Evolution] Mídia baixada: {len(base64_data)} caracteres, tipo: {mimetype}")
                return {
                    'base64': base64_data,
                    'mimetype': mimetype
                }
            else:
                logger.warning(f"[Evolution] Resposta sem base64: {list(data.keys())}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[Evolution] Erro ao baixar mídia: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[Evolution] Erro inesperado ao baixar mídia: {str(e)}")
            return None

    @staticmethod
    def identify_and_link_message(message_obj):
        """Tenta identificar Lead ou Oportunidade pelo número da mensagem e vincula"""
        # Pega o número remoto (remetente ou destinatário que não seja a instância)
        remote_number = message_obj.numero_remetente if not message_obj.de_mim else message_obj.numero_destinatario
        
        if not remote_number:
            return

        # Limpa o número: remove '@s.whatsapp.net' e caracteres não numéricos
        clean_num = str(remote_number).split('@')[0]
        clean_num = ''.join(filter(str.isdigit, clean_num))
        
        if not clean_num or len(clean_num) < 8:
            return
        
        # Gera TODAS as variações possíveis do número
        variations = set()
        
        # Número original
        variations.add(clean_num)
        
        # Remove DDI 55 se existir
        base_num = clean_num[2:] if clean_num.startswith('55') else clean_num
        variations.add(base_num)
        
        # Adiciona DDI 55 se não tiver
        if not clean_num.startswith('55'):
            variations.add('55' + clean_num)
        
        # Gera variações com/sem o 9º dígito para cada variação base
        for num in list(variations):
            # Formato: DDD (2) + 9 (1) + número (8) = 11 dígitos (sem DDI)
            # Formato: 55 + DDD (2) + 9 (1) + número (8) = 13 dígitos (com DDI)
            
            if num.startswith('55'):
                ddd = num[2:4]  # Pega DDD
                rest = num[4:]  # Resto do número
                
                if len(rest) == 9 and rest.startswith('9'):
                    # Tem 9, gera sem
                    variations.add('55' + ddd + rest[1:])
                    variations.add(ddd + rest[1:])
                elif len(rest) == 8:
                    # Não tem 9, gera com
                    variations.add('55' + ddd + '9' + rest)
                    variations.add(ddd + '9' + rest)
            else:
                if len(num) >= 10:
                    ddd = num[0:2]
                    rest = num[2:]
                    
                    if len(rest) == 9 and rest.startswith('9'):
                        # Tem 9, gera sem
                        variations.add(ddd + rest[1:])
                        variations.add('55' + ddd + rest[1:])
                    elif len(rest) == 8:
                        # Não tem 9, gera com
                        variations.add(ddd + '9' + rest)
                        variations.add('55' + ddd + '9' + rest)
        
        # Adiciona os últimos 8 dígitos como fallback (mais agressivo)
        if len(clean_num) >= 8:
            variations.add(clean_num[-8:])
        
        # logger.debug(f"[Evolution] Variações geradas para {remote_number}: {variations}")
        
        # Filtros de busca para Lead
        q_filter = Q()
        for v in variations:
            if len(v) >= 8:
                q_filter |= Q(telefone__icontains=v)
            
        # Tenta Lead
        lead = Lead.objects.filter(q_filter).first()
        if lead:
            message_obj.lead = lead
            
        # Tenta Oportunidade (via contato principal)
        q_opp = Q()
        for v in variations:
            if len(v) >= 8:
                q_opp |= Q(contato_principal__telefone__icontains=v) | \
                         Q(contato_principal__celular__icontains=v)
            
        opp = Oportunidade.objects.filter(q_opp).first()
        if opp:
            message_obj.oportunidade = opp
            
        message_obj.save()

