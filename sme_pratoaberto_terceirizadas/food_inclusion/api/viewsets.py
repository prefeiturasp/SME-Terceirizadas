from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.food_inclusion.api.serializers import FoodInclusionSerializer
from sme_pratoaberto_terceirizadas.food_inclusion.errors import FoodInclusionCreateOrUpdateException
from sme_pratoaberto_terceirizadas.food_inclusion.models import FoodInclusion, FoodInclusionStatus
from sme_pratoaberto_terceirizadas.food_inclusion.utils import get_errors_list, check_required_data_generic
from sme_pratoaberto_terceirizadas.users.models import User


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
        errors_list = list()
        try:
            user = get_object_or_404(User, uuid=pk)
            errors_list = get_errors_list(request.data)
            if errors_list:
                raise FoodInclusionCreateOrUpdateException(_('some argument(s) is(are) not valid'))
            uuid = request.data.get('uuid', None)
            food_inclusion = get_object_or_404(FoodInclusion, uuid=uuid) if uuid else FoodInclusion()
            if uuid:
                assert food_inclusion.status == FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_EDIT), \
                    _('food inclusion status is not to edit')
            food_inclusion.create_or_update(request_data=request.data, user=user)
            validation_diff = 'creation' if not uuid else 'edition'
            food_inclusion.send_notification(user, validation_diff)
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('food inclusion not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except FoodInclusionCreateOrUpdateException:
            response['log_content'] = errors_list
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])

    @detail_route(methods=['post'], permission_classes=[])
    def validate(self, request, pk=None):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = get_object_or_404(User, uuid=pk)
            assert check_required_data_generic(request.data, ['uuid', 'validation_answer']), \
                _('missing arguments')
            validation_answer = request.data.get('validation_answer')
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(FoodInclusion, uuid=uuid)
            assert food_inclusion.status == FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_VALIDATE), \
                _('food inclusion status is not to validate')
            new_status = FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_APPROVE) if validation_answer \
                else FoodInclusionStatus.objects.get(FoodInclusionStatus.TO_EDIT)
            food_inclusion.status = new_status
            food_inclusion.save()
            food_inclusion.send_notification(user)
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('food inclusion not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except AssertionError as assertionError:
            response['log_content'] = str(assertionError)
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])

    @detail_route(methods=['post'], permission_classes=[])
    def approve(self, request, pk=None):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = get_object_or_404(User, uuid=pk)
            approval_answer = request.data.get('approval_answer')
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(FoodInclusion, uuid=uuid)
            assert food_inclusion.status == FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_APPROVE), \
                _('food inclusion status is not to approve')
            new_status = FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_VISUALIZE) if approval_answer \
                else FoodInclusionStatus.objects.get(name=FoodInclusionStatus.DENIED)
            food_inclusion.status = new_status
            food_inclusion.save()
            food_inclusion.send_notification(user)
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('food inclusion not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except FoodInclusionCreateOrUpdateException:
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])

    @detail_route(methods=['post'], permission_classes=[])
    def visualize(self, request, pk=None):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = get_object_or_404(User, uuid=pk)
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(FoodInclusion, uuid=uuid)
            assert food_inclusion.status == FoodInclusionStatus.objects.get(name=FoodInclusionStatus.TO_VISUALIZE), \
                _('food inclusion status is not to visualize')
            new_status = FoodInclusionStatus.objects.get(name=FoodInclusionStatus.VISUALIZED)
            food_inclusion.status = new_status
            food_inclusion.save()
            food_inclusion.send_notification(user)
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('food inclusion not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except FoodInclusionCreateOrUpdateException:
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])
