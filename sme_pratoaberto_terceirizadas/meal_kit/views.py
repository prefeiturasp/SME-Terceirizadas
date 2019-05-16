from django.utils.translation import ugettext_lazy as _
from notifications.signals import notify
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import MealKit
from .serializers import MealKitSerializer
from ..users.models import User
from ..users.serializers import PrivateUserSerializer


class MealKitViewSet(ModelViewSet):
    """
    Endpoint para Solicitações de Kit Lanches
    """
    queryset = User.objects.all()
    serializer_class = MealKitSerializer
    object_class = User
    permission_classes = ()

    @detail_route(methods=['post'], permission_classes=[])
    def meal_kit_solicitation(self, request, pk=None):
        """
        {
            "name": "Kit Lanche 1",
            "description: "Kit Lanche para a escola x"
        }
        """
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = User.objects.get(uuid=pk)
            new_meal_kit = MealKit()
            new_meal_kit.name = request.data.get('name')
            new_meal_kit.description = request.data.get('description')
            new_meal_kit.save()
            actor = user
            action_object = new_meal_kit
            notify.send(
                sender=actor,
                verb=_('Meal Kit - Solicitation'),
                action_object=action_object,
                description='O usuário ' + actor.name + ' solicitou um kit lanche para o dia 20/06/2019')
        except Exception:
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['user'] = PrivateUserSerializer(user).data
        return Response(response, status=response['code'])
