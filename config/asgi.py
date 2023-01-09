"""
ASGI config for SME-Terceirizadas project.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from sme_terceirizadas.dados_comuns.urls import ws_urlpatterns

# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *ws_urlpatterns
        ])
    ),
})
