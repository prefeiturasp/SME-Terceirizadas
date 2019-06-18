from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.food_inclusion.api.serializers import FoodInclusionSerializer, \
    FoodInclusionReasonSerializer
from sme_pratoaberto_terceirizadas.food_inclusion.errors import FoodInclusionCreateOrUpdateException
from sme_pratoaberto_terceirizadas.food_inclusion.models import InclusaoAlimentacao, InclusaoAlimentacaoStatus, MotivoInclusaoAlimentacao
from sme_pratoaberto_terceirizadas.food_inclusion.utils import obter_lista_erros, checar_dados_genericos_requeridos
from sme_pratoaberto_terceirizadas.users.models import User


class FoodInclusionViewSet(ModelViewSet):
    """
    Endpoint para Inclusão de Alimentação
    """
    queryset = InclusaoAlimentacao.objects.all()
    serializer_class = FoodInclusionSerializer
    object_class = InclusaoAlimentacao

    @action(detail=False, methods=['get'])
    def get_reasons(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            reasons_simple = MotivoInclusaoAlimentacao.objects.exclude(name__icontains='Programa Contínuo').filter(
                is_active=True)
            reasons_continuous_program = MotivoInclusaoAlimentacao.objects.filter(name__icontains='Programa Contínuo',
                                                                            is_active=True)
        except Http404:
            response['log_content'] = ["Usuário não encontrado"]
            response['code'] = status.HTTP_404_NOT_FOUND
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['reasons_simple'] = FoodInclusionReasonSerializer(reasons_simple, many=True).data
            response['content']['reasons_continuous_program'] = FoodInclusionReasonSerializer(
                reasons_continuous_program, many=True).data
        return Response(response, status=response['code'])

    @action(detail=False, methods=['get'])
    def get_saved_food_inclusions(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = request.user
            food_inclusions = InclusaoAlimentacao.objects.filter(status__name=InclusaoAlimentacaoStatus.SAVED, created_by=user)
        except Http404:
            response['log_content'] = ["Usuário não encontrado"]
            response['code'] = status.HTTP_404_NOT_FOUND
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusions'] = FoodInclusionSerializer(food_inclusions, many=True).data
        return Response(response, status=response['code'])

    @action(detail=False, methods=['post'])
    def create_or_update(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        errors_list = list()
        try:
            user = request.user
            errors_list = obter_lista_erros(request.data)
            if errors_list:
                raise FoodInclusionCreateOrUpdateException(_('some argument(s) is(are) not valid'))
            uuid = request.data.get('uuid', None)
            food_inclusion = get_object_or_404(InclusaoAlimentacao, uuid=uuid) if uuid else InclusaoAlimentacao()
            if uuid:
                assert food_inclusion.status in [InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_EDIT),
                                                 InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.SAVED)], \
                    "Inclusão de Alimentação não está com status válido para edição"
                food_inclusion.foodinclusiondescription_set.all().delete()
                food_inclusion.foodinclusiondayreason_set.all().delete()
            food_inclusion.criar_ou_alterar(request_data=request.data, user=user)
            validation_diff = 'creation' if not uuid else 'edition'
            if food_inclusion.status.name != InclusaoAlimentacaoStatus.SAVED:
                food_inclusion.enviar_notificacao(user, validation_diff)
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('food inclusion not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except AssertionError as error:
            response['log_content'] = [str(error)]
            response['code'] = status.HTTP_400_BAD_REQUEST
        except FoodInclusionCreateOrUpdateException:
            response['log_content'] = errors_list
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['food_inclusion'] = FoodInclusionSerializer(food_inclusion).data
        return Response(response, status=response['code'])

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = request.user
            uuid = request.data.get('uuid', None)
            food_inclusion = get_object_or_404(InclusaoAlimentacao, uuid=uuid, created_by=user)
            assert food_inclusion.status == InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.SAVED), \
                "Status de inclusão não está como SALVO"
            food_inclusion.delete()
        except Http404 as error:
            response['log_content'] = ['Usuário não encontrado'] if 'User' in str(error) else [
                'Inclusão de alimentação não encontrada']
            response['code'] = status.HTTP_404_NOT_FOUND
        except AssertionError as error:
            response['code'] = status.HTTP_400_BAD_REQUEST
            response['log_content'] = [str(error)]
        else:
            response['code'] = status.HTTP_200_OK
        return Response(response, status=response['code'])

    @action(detail=False, methods=['post'])
    def validate(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = request.user
            assert checar_dados_genericos_requeridos(request.data, ['uuid', 'validation_answer']), \
                _('missing arguments')
            validation_answer = request.data.get('validation_answer')
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
            assert food_inclusion.status == InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_VALIDATE), \
                _('food inclusion status is not to validate')
            new_status = InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_APPROVE) if validation_answer \
                else InclusaoAlimentacaoStatus.objects.get(InclusaoAlimentacaoStatus.TO_EDIT)
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

    @action(detail=False, methods=['post'])
    def approve(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = request.user
            approval_answer = request.data.get('approval_answer')
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
            assert food_inclusion.status == InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_APPROVE), \
                _('food inclusion status is not to approve')
            new_status = InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_VISUALIZE) if approval_answer \
                else InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.DENIED_BY_CODAE)
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

    @action(detail=False, methods=['post'])
    def visualize(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = request.user
            uuid = request.data.get('uuid')
            food_inclusion = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
            assert food_inclusion.status == InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.TO_VISUALIZE), \
                _('food inclusion status is not to visualize')
            accepted_by_company = request.data.get('accepted_by_company', True)
            if accepted_by_company:
                new_status = InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.VISUALIZED)
            else:
                new_status = InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.DENIED_BY_COMPANY)
                food_inclusion.denial_reason = request.data.get('denial_reason')
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
