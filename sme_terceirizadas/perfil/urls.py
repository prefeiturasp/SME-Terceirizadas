from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('cadastro', viewsets.UsuarioUpdateViewSet, 'Cadastro de Usuários')
router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('grupos-perfis', viewsets.GrupoPerfilViewSet, 'Grupos de Perfis')
router.register('permissoes', viewsets.PermissaoViewSet, 'Permissões')
router.register('permissoes-acoes', viewsets.AcoesViewSet, 'Ações')
router.register('perfis-permissoes', viewsets.PerfilPermissaoViewSet, 'Perfis permissões')
router.register('notificacoes', viewsets.NotificationViewSet, 'Notificações')
router.register('confirmar_email/(?P<uuid>[^/]+)/(?P<confirmation_key>[^/]+)',
                viewsets.UsuarioConfirmaEmailViewSet, 'Confirmar E-mail')

urlpatterns = [
    path('', include(router.urls))
]
