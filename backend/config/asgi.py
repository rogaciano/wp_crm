"""
ASGI config for CRM project — suporta HTTP e WebSocket (Django Channels).

IMPORTANTE: get_asgi_application() DEVE ser chamado antes de qualquer import
do crm.* para garantir que o AppRegistry do Django esteja pronto.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 1. Inicializa o Django PRIMEIRO — isso popula o AppRegistry
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 2. SÓ DEPOIS importa os módulos que dependem do Django estar pronto
from channels.routing import ProtocolTypeRouter, URLRouter
from crm.ws_middleware import JWTAuthMiddleware
from crm.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
