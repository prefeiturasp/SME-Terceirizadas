from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('grupos-perfis', viewsets.GrupoPerfilViewSet, 'Grupos de Perfis')

urlpatterns = [
    path('', include(router.urls))
]
