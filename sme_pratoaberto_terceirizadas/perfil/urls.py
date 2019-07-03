from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('usuarios', viewsets.UsuarioViewSet, base_name='usuarios')
router.register('perfis', viewsets.PerfilViewSet, base_name='perfis')
router.register('grupos-perfis', viewsets.GrupoPerfilViewSet, base_name='grupos-perfis')

urlpatterns = [
    path('', include(router.urls))
]
