"""
ASGI config for CRM project — supports HTTP and WebSocket (Django Channels).
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = None

def get_application():
    from django.core.asgi import get_asgi_application
    from channels.routing import ProtocolTypeRouter, URLRouter
    from crm.ws_middleware import JWTAuthMiddleware
    from crm.routing import websocket_urlpatterns

    return ProtocolTypeRouter({
        'http': get_asgi_application(),
        'websocket': JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    })

application = get_application()
