from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer
from sme_pratoaberto_terceirizadas.school.models import School
from ..models import MealKit, OrderMealKit


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

    def create(self, request):

        school = School.objects.filter(users=request.user).first()

        if not school:
            return Response({'detail': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)

        if self._validar_duplicidade(request.data, school):
            return self._enviar_solicitacao_kit_lanche(request.data, school)

        return Response({'detail': 'A Solicitação já foi cadastrada no sistema'}, status=status.HTTP_400_BAD_REQUEST)

    def _validar_duplicidade(self, data, school):

        data_passeio = datetime.strptime(data['evento_data'], '%d/%m/%Y')

        if OrderMealKit.objects.filter(schools=school, order_date=data_passeio):
            return False

        return True

    def _enviar_solicitacao_kit_lanche(self, params, school):

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

            solicitacao.schools.add(school)
            for m in meals:
                solicitacao.meal_kits.add(m)

            solicitacao.save()

            return Response({'details': response_message}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'details': 'Erro ao tentar salvar solicitação'}, status=status.HTTP_502_BAD_GATEWAY)

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

    def _disparar_notificacao(self, data):
        pass
