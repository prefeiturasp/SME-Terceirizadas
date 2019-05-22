from django.urls import path, include
from rest_framework import routers

from sme_pratoaberto_terceirizadas.food.api.viewsets import MealViewSet

router = routers.DefaultRouter()
router.register('refeicao', MealViewSet)

urlpatterns = [
    path('', include(router.urls))
]
