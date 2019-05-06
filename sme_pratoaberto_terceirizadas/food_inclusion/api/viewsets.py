from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.food_inclusion.api.serializers import FoodInclusionSerializer
from sme_pratoaberto_terceirizadas.food_inclusion.models import FoodInclusion
from sme_pratoaberto_terceirizadas.food_inclusion.utils import create_notification, get_errors_list, get_object
from sme_pratoaberto_terceirizadas.users.models import User


class FoodInclusionCreateOrUpdateException(Exception):
    pass


class FoodInclusionViewSet(ModelViewSet):
    """
    Endpoint para Inclusão de Alimentação
    """
    queryset = FoodInclusion.objects.all()
    serializer_class = FoodInclusionSerializer
    object_class = FoodInclusion
    permission_classes = ()

    @detail_route(methods=['post'], permission_classes=[])
    def create_or_update(self, request, pk=None):
        response = {'content': {}, 'log_content': {}, 'code': None}
        errors_list = []
        try:
            user = get_object_or_404(User, uuid=pk)
            errors_list = get_errors_list(request.data)
            if errors_list:
                raise FoodInclusionCreateOrUpdateException(_('some argument(s) are not valid'))
            uuid = request.data.get('uuid', None)
            food_inclusion = get_object(FoodInclusion, uuid=uuid) if uuid else FoodInclusion()
            food_inclusion.create_or_update(request_data=request.data, user=user)
            create_notification(user=user, obj=food_inclusion)
        except Http404:
            response['log_content'] = [_('user not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except FoodInclusionCreateOrUpdateException:
            response['log_content'] = errors_list
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])

    # @detail_route(methods=['post'], permission_classes=[])
    # def
