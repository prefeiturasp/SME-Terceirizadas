from django.urls import path, include
from rest_framework import routers

from .api import viewsets
from .views import send_test_email

router = routers.DefaultRouter()
router.register('email', viewsets.ConfiguracaoEmailViewSet, basename='email')
router.register('dias-semana', viewsets.DiasDaSemanaViewSet, basename='dias-semana')
router.register('dias-uteis', viewsets.DiasUteisViewSet, basename='dias-uteis')

urlpatterns = [
    path("", include(router.urls)),
    path("email-teste/", send_test_email, name="enviar_email_teste")
]
