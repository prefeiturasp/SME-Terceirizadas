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
from sme_pratoaberto_terceirizadas.utils import send_notification


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

    def destroy(self, request, pk=None):
        solicitacao = OrderMealKit.objects.get(pk=request.data['id'])
        if solicitacao:
            solicitacao.delete()
            return Response({'detail': 'Solicitação removida com sucesso.'})
        else:
            return Response({'detail': 'Solicitação não encontrada'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs, ):

        data = request.data
        data_passeio = datetime.strptime(data['evento_data'], '%d/%m/%Y').date()
        meals = MealKit.objects.filter(meals__uuid__in=data['kit_lanche'])

        solicitacao = OrderMealKit.objects.get(pk=pk)
        if solicitacao:
            solicitacao.location = data['local_passeio']
            solicitacao.students_quantity = data['nro_alunos']
            solicitacao.order_date = data_passeio
            solicitacao.observation = data['obs'],
            solicitacao.status = 'SAVED'
            solicitacao.scheduled_time = data['tempo_passeio']
            for m in meals:
                solicitacao.meal_kits.add(m)
            solicitacao.save()

            return Response({'details': 'Solicitação atualizada com sucesso'})
        return Response({'details': 'Solicitação não encontrada'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        escola = self._valida_escola(request.user)

        # lote_solicitacoes = self._checa_solicitacoes_is_lote(request.data, escola)

        if self._validar_duplicidade(request.data, escola):
            return self._enviar_solicitacao_kit_lanche(request.data, escola)

        return Response({'detail': 'A Solicitação já foi cadastrada no sistema'}, status=status.HTTP_400_BAD_REQUEST)

    def _valida_escola(self, user: User):
        escola = School.objects.filter(users=user).first()

        if not escola:
            return Response({'detail': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)
        return escola

    def _validar_duplicidade(self, data, escolas, status='SAVED'):

        data_passeio = datetime.strptime(data['evento_data'], '%d/%m/%Y')

        if OrderMealKit.objects.filter(schools=escolas, order_date=data_passeio, status=status):
            return False

        return True

    def _enviar_solicitacao_kit_lanche(self, params, escola):

        try:
            data_passeio = datetime.strptime(params['evento_data'], '%d/%m/%Y').date()

            meals = MealKit.objects.filter(uuid__in=params['kit_lanche'])

            if 'Acao' in params:
                status_solicitacao = 'SENDED'
                response_message = 'Solicitação em fase de aprovação'
            else:
                status_solicitacao = 'SAVED'
                response_message = 'Solicitação salva com sucesso'

            solicitacao = OrderMealKit(
                location=params['local_passeio'],
                students_quantity=params['nro_alunos'],
                order_date=data_passeio,
                observation=params['obs'],
                status=status_solicitacao,
                scheduled_time=params['tempo_passeio']
            )
            solicitacao.save()

            solicitacao.schools.add(escola)
            for m in meals:
                solicitacao.meal_kits.add(m)

            solicitacao.save()

            return Response({'details': response_message}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'details': 'Erro ao tentar salvar solicitação'}, status=status.HTTP_502_BAD_GATEWAY)

    def _checa_solicitacoes_is_lote(self, request, usuario):
        if 'ids' in request:
            solicitacoes = OrderMealKit.objects.filter(pk__in=request['ids'])

        if solicitacoes:
            for solicitacao in solicitacoes:
                solicitacao.status = 'SENDED'
                solicitacao.save()
                send_notification(usuario, User.objects.filter(email='mmaia.cc@gmail.com'), 'Teste de nofiticação', 'Teste de nofiticação')
            return Response({'details': 'Solicitações enviadas com sucesso.'})
        return Response({'details': 'Nenhuma soliciação encontrada'})

    @action(detail=False, methods=['post'])
    def solicitacoes(self, request):
        return self._checa_solicitacoes_is_lote(request.data, request.user)
