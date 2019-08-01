from django.urls import path, include
from rest_framework import routers

from .api import viewsets
from .views import send_test_email

router = routers.DefaultRouter()
router.register('email', viewsets.ConfiguracaoEmailViewSet, basename='Email')
router.register('dias-semana', viewsets.DiasDaSemanaViewSet, basename='Dias da semana')
router.register('tempos-passeio', viewsets.TempoDePasseioViewSet, basename='Tempos de passeio')
router.register('dias-uteis', viewsets.DiasUteisViewSet, basename='Dias úteis')
router.register('templates-mensagem', viewsets.ConfiguracaoMensagemViewSet,
                basename='Configuração de mensagem')

urlpatterns = [
    path("", include(router.urls)),
    path("email-teste/", send_test_email, name="enviar_email_teste")
]
