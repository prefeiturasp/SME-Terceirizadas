from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('cadastro', viewsets.UsuarioUpdateViewSet, 'Cadastro de Usuários')
router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('notificacoes', viewsets.NotificationViewSet, 'Notificações')


urlpatterns = [
    path('', include(router.urls))
]
