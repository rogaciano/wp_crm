import requests
import json
import logging
from django.conf import settings
from datetime import datetime
from ..models import WhatsappMessage, Lead, Oportunidade
from django.db.models import Q

logger = logging.getLogger(__name__)

class EvolutionService:
    def __init__(self):
        self.api_key = settings.EVOLUTION_API_KEY.strip()
        self.base_url = settings.EVOLUTION_API_URL.strip().rstrip('/')
        self.instance = settings.EVOLUTION_INSTANCE_ID.strip()
        self.headers = {
            'apikey': self.api_key,
            'apiKey': self.api_key,  # Alguns usam Case Sensitive
            'Content-Type': 'application/json'
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

    @staticmethod
    def identify_and_link_message(message_obj):
        """Tenta identificar Lead ou Oportunidade pelo número da mensagem e vincula"""
        # Pega o número remoto (remetente ou destinatário que não seja a instância)
        remote_number = message_obj.numero_remetente if not message_obj.de_mim else message_obj.numero_destinatario
        
        if not remote_number:
            return

        # Limpa o número para buscar no banco
        clean_num = ''.join(filter(str.isdigit, str(remote_number)))
        
        # Cria variações para busca (com e sem 55, com e sem 9o dígito)
        variations = [clean_num]
        if clean_num.startswith('55') and len(clean_num) >= 12:
            variations.append(clean_num[2:])
            if len(clean_num) == 13: # Com 9o dígito
                variations.append(clean_num[:4] + clean_num[5:]) # Sem 9
            elif len(clean_num) == 12: # Sem 9o dígito
                variations.append(clean_num[:4] + '9' + clean_num[4:]) # Com 9
        
        # Monta a query para Lead
        q_lead = Q()
        for v in variations:
            q_lead |= Q(telefone__icontains=v)
            
        lead = Lead.objects.filter(q_lead).first()
        if lead:
            message_obj.lead = lead
            
        # Monta a query para Oportunidade (via contato principal)
        q_opp = Q()
        for v in variations:
            q_opp |= Q(contato_principal__telefone__icontains=v) | Q(contato_principal__celular__icontains=v)
            
        opp = Oportunidade.objects.filter(q_opp).first()
        if opp:
            message_obj.oportunidade = opp
            
        message_obj.save()

