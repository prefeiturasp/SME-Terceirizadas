from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer
from sme_pratoaberto_terceirizadas.school.models import School
from sme_pratoaberto_terceirizadas.users.models import User
from ..models import MealKit, OrderMealKit
from .validators import valida_usuario_escola


class MealKitViewSet(ModelViewSet):
    """ Endpoint para visualização de Kit Lanches """
    queryset = MealKit.objects.all()
    serializer_class = MealKitSerializer
    # permission_classes = (IsAuthenticated, ValidatePermission)

    @action(detail=False)
    def students(self, request):
        return Response({'students': 200}, status=status.HTTP_200_OK)


class OrderMealKitViewSet(ModelViewSet):
    """ Endpoint para Solicitações de Kit Lanches """
    serializer_class = OrderMealKitSerializer
    # permission_classes = (IsAuthenticated, ValidatePermission)

    def get_queryset(self):
        return OrderMealKit.objects.filter(status='SAVED')

    def destroy(self, request, *args, **kwargs):
        response = super(OrderMealKitViewSet, self).destroy(request, *args, **kwargs)
        if response.status_code == 204:
            return Response({'success': 'Solicitação removida com sucesso.'})
        return Response({'error': 'Solicitação não encontrada'}, status=status.HTTP_409_CONFLICT)

    def create(self, request):
        escola = self._valida_escola(request.user)
        if OrderMealKit.valida_duplicidade(request.data, escola):
            if OrderMealKit.solicitar_kit_lanche(request.data, escola, request.user):
                return Response({'success': 'Sua solicitação foi enviada com sucesso'}, status=status.HTTP_201_CREATED)
            return Response({'error': 'Erro ao tentar salvar solicitação, tente novamente'},
                            status=status.HTTP_502_BAD_GATEWAY)
        return Response({'error': 'Solicitação já cadastrada no sistema com esta data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def _valida_escola(self, user: User):
        escola = School.objects.filter(users=user).first()
        if not escola:
            return Response({'error': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)
        return escola

    @action(detail=False, methods=['post'])
    def solicitacoes(self, request):
        resposta = OrderMealKit.solicita_kit_lanche_em_lote(request.data, request.user)
        if resposta is False:
            return Response({'error': 'Ocorreu um error na solicitação em massa, tente novamente'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': '{} solicitações enviada com sucesso.'.format(resposta)})

    @action(detail=False, methods=['post'])
    def salvar(self, request):
        params = request.data
        escola = School.objects.filter(users=request.user).first()
        if not valida_usuario_escola(request.user):
            return Response({'error': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)

        if OrderMealKit.ja_existe_salvo(params, escola) and not params.get('id', None):
            return Response({'error': 'Já existe um evento cadastrado para esta data'},
                            status=status.HTTP_400_BAD_REQUEST)
        OrderMealKit.salvar_solicitacao(params, escola)
        return Response({'success': 'Solicitação salva com sucesso'})
