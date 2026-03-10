"""
WebSocket Consumer para o módulo de Multiatendimento WhatsApp.

Cada canal (Canal model) tem sua própria sala WebSocket:
  Grupo: "atendimento_canal_{canal_id}"
  URL:   ws/atendimento/{canal_id}/

Ao receber uma nova WhatsappMessage pelo webhook, o signal
notifica o grupo do canal correspondente via channel_layer.group_send().
"""

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class AtendimentoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        canal_id = self.scope['url_route']['kwargs']['canal_id']

        # Rejeita conexões não autenticadas
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # Rejeita se o usuário não tem permissão para este canal
        # Admin pode ver qualquer canal; outros só o próprio
        if not await self.can_access_canal(user, canal_id):
            await self.close(code=4003)
            return

        self.canal_id = canal_id
        self.group_name = f'atendimento_canal_{canal_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f'[WS] {user.username} conectou ao canal {canal_id}')

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f'[WS] Desconectou do canal {self.canal_id} (code={close_code})')

    # Mensagem enviada pelo grupo (via signal/webhook) → encaminha para o client
    async def nova_mensagem(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'nova_mensagem',
            'conversa': event['conversa'],
        }))

    # Notificação de contagem de não lidas atualizada
    async def unread_update(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'unread_update',
            'numero': event['numero'],
            'canal_id': event['canal_id'],
            'nao_lidas': event['nao_lidas'],
        }))

    @database_sync_to_async
    def can_access_canal(self, user, canal_id):
        from crm.models import Canal
        # Admin pode acessar qualquer canal
        if user.perfil == 'ADMIN' or user.is_superuser:
            return Canal.objects.filter(id=canal_id).exists()
        # Demais usuários só acessam o próprio canal
        return str(getattr(user.canal, 'id', None)) == str(canal_id)
