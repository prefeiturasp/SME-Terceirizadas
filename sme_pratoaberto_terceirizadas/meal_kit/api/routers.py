from django.urls import path, include
from rest_framework import routers
from .viewsets import MealKitViewSet, OrderMealKitViewSet

router = routers.DefaultRouter()

router.register('kit-lanche', MealKitViewSet, base_name='meal_kit')
router.register('solicitar-kit-lanche', OrderMealKitViewSet, base_name='order_meal_kit')

urlpatterns = [
    path('', include(router.urls))
]
