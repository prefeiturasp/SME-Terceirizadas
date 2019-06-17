from django.urls import path, include
from rest_framework import routers

from sme_pratoaberto_terceirizadas.alimento.api.viewsets import RefeicaoViewSet

router = routers.DefaultRouter()
router.register('refeicao', RefeicaoViewSet)

urlpatterns = [
    path('', include(router.urls))
]
