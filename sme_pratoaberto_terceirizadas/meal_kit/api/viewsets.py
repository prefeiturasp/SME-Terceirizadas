from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from sme_pratoaberto_terceirizadas.permission.permissions import ValidatePermission
from ..models import MealKit, OrderMealKit

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer
from sme_pratoaberto_terceirizadas.users.models import User


class MealKitViewSet(ModelViewSet):
    """
    Endpoint para Solicitações de Kit Lanches
    """
    queryset = MealKit.objects.all()
    serializer_class = MealKitSerializer
    # object_class = User
    # permission_classes = (IsAuthenticated, ValidatePermission)


class OrderMealKitViewSet(ModelViewSet):
    queryset = OrderMealKit.objects.all()
    serializer_class = OrderMealKitSerializer
