from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from sme_pratoaberto_terceirizadas.permission.permissions import ValidatePermission
from ..models import MealKit, OrderMealKit

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer


class MealKitViewSet(ModelViewSet):
    """ Endpoint para visualização de Kit Lanches """
    queryset = MealKit.objects.all()
    serializer_class = MealKitSerializer
    # permission_classes = (IsAuthenticated, ValidatePermission)

    @action(detail=False)
    def students(self, request):
        user = request.user
        print(user.email)
        return Response({'students': 300}, status=status.HTTP_200_OK)


class OrderMealKitViewSet(ModelViewSet):
    """ Endpoint para Solicitações de Kit Lanches """
    queryset = OrderMealKit.objects.all()
    serializer_class = OrderMealKitSerializer
    permission_classes = (IsAuthenticated, ValidatePermission)
