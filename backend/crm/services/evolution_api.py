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
            
            # Tenta salvar localmente para histórico imediato (opcional, pode vir via webhook tb)
            # Mas salvando aqui garante que o usuário veja que enviou mesmo se o webhook demorar
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
        
        # Limpa o número para buscar no banco (removendo 55 se houver pra facilitar busca flexível)
        clean_num = remote_number
        if clean_num.startswith('55'):
            clean_num = clean_num[2:]
            
        # Busca Lead
        lead = Lead.objects.filter(
            Q(telefone__icontains=clean_num) | Q(telefone__icontains=remote_number)
        ).first()
        
        if lead:
            message_obj.lead = lead
            
        # Busca Oportunidade (via contato principal)
        opp = Oportunidade.objects.filter(
            Q(contato_principal__telefone__icontains=clean_num) | 
            Q(contato_principal__telefone__icontains=remote_number)
        ).first()
        
        if opp:
            message_obj.oportunidade = opp
            
        message_obj.save()
