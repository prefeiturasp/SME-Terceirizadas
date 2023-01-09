"""
ASGI config for SME-Terceirizadas project.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production') # noqa I001
django.setup() # noqa I001
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from sme_terceirizadas.dados_comuns.urls import ws_urlpatterns
# noqa I003
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *ws_urlpatterns
        ])
    ),
})
