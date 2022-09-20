from django.urls import include, path
from rest_framework import routers

from .api import viewsets
from .api.login import LoginView

router = routers.DefaultRouter()

router.register('cadastro', viewsets.UsuarioUpdateViewSet, 'Cadastro de Usuários')
router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('vinculos', viewsets.VinculoViewSet, 'Vinculos')
router.register('confirmar_email/(?P<uuid>[^/]+)/(?P<confirmation_key>[^/]+)',
                viewsets.UsuarioConfirmaEmailViewSet, 'Confirmar E-mail')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
]
