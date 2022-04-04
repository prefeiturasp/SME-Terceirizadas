from django.urls import include, path
from rest_framework import routers

from .api import viewsets
from .views import send_test_email, test_visualiza_email

router = routers.DefaultRouter()
router.register('api-version', viewsets.ApiVersion, basename='Version')
router.register('email', viewsets.ConfiguracaoEmailViewSet, basename='Email')
router.register('dias-semana', viewsets.DiasDaSemanaViewSet, basename='Dias da semana')
router.register('tempos-passeio', viewsets.TempoDePasseioViewSet, basename='Tempos de passeio')
router.register('dias-uteis', viewsets.DiasUteisViewSet, basename='Dias úteis')
router.register('templates-mensagem', viewsets.TemplateMensagemViewSet,
                basename='Configuração de mensagem')
router.register('perguntas-frequentes', viewsets.PerguntaFrequenteViewSet, basename='Perguntas Frequentes')
router.register('categorias-pergunta-frequente', viewsets.CategoriaPerguntaFrequenteViewSet,
                basename='Categorias de Pergunta Frequente')
router.register('notificacoes', viewsets.NotificacaoViewSet, basename='Notificações')
router.register('downloads', viewsets.CentralDeDownloadViewSet, basename='Downloads')

urlpatterns = [
    path('', include(router.urls)),
    path('email-teste/', send_test_email, name='enviar_email_teste'),
    path('visualiza-email/', test_visualiza_email, name='email_teste')
]
