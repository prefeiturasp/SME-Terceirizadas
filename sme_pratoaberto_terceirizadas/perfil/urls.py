from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('grupos-perfis', viewsets.GrupoPerfilViewSet, 'Grupos de Perfis')
router.register('permissoes', viewsets.PermissaoViewSet, 'Permissões')
router.register('acoes', viewsets.AcoesViewSet, 'Ações')
router.register('perfis-permissoes', viewsets.PerfilPermissaoViewSet, 'Perfis permissões')

urlpatterns = [
    path('', include(router.urls))
]
