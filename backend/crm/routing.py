"""
WebSocket URL routing for CRM Channels.
"""

from django.urls import re_path
from crm import consumers

websocket_urlpatterns = [
    re_path(r'^ws/atendimento/(?P<canal_id>\d+)/$', consumers.AtendimentoConsumer.as_asgi()),
]
