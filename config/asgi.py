"""
ASGI config for SME-Terceirizadas project.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from channels.auth import AuthMiddlewareStack  # noqa
from channels.http import AsgiHandler  # noqa
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from sme_terceirizadas.dados_comuns.urls import ws_urlpatterns  # noqa


# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.

application = ProtocolTypeRouter({
    'http': AsgiHandler(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *ws_urlpatterns
        ])
    ),
})
