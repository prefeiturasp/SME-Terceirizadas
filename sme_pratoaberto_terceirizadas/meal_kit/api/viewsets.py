from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from sme_pratoaberto_terceirizadas.permission.permissions import ValidatePermission
from sme_pratoaberto_terceirizadas.school.models import School
from ..models import MealKit, OrderMealKit

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer


class MealKitViewSet(ModelViewSet):
    """ Endpoint para visualização de Kit Lanches """
    queryset = MealKit.objects.all()
    serializer_class = MealKitSerializer

    # permission_classes = (IsAuthenticated, ValidatePermission)

    @action(detail=False)
    def students(self, request):
        return Response({'students': 300}, status=status.HTTP_200_OK)


class OrderMealKitViewSet(ModelViewSet):
    """ Endpoint para Solicitações de Kit Lanches """
    queryset = OrderMealKit.objects.all()
    serializer_class = OrderMealKitSerializer

    # permission_classes = (IsAuthenticated, ValidatePermission)

    def create(self, request, *args, **kwargs):

        school = School.objects.filter(users=request.user).first()

        if not school:
            return Response({'detail': 'Sem escola relacinada a este usuário'})

        if self._validar_duplicidade(request.data, school):
            return self._salvar_solicitacao_kit_lanche(request.data, school)

        return Response({'detail': 'A Solicitação já foi cadastrada no sistema'}, status=status.HTTP_400_BAD_REQUEST)

    def _validar_duplicidade(self, data, school):
        data_passeio = datetime.strptime(data['evento_data'], '%d/%m/%Y')

        if OrderMealKit.objects.filter(schools=school, order_date=data_passeio):
            return False

        return True

    def _salvar_solicitacao_kit_lanche(self, data, school):
        data_passeio = datetime.strptime(data['evento_data'], '%d/%m/%Y').date()

        solicitacao = OrderMealKit(
            location=data['local_passeio'],
            students_quantity=['nro_alunos'],
            order_date=data_passeio,
            observation=['obs'],
            status='SENDED',
            schools=school,
            meal_kits=MealKit.objects.filter(meals__uuid__in=data['kit_lanche'])
        )

        print(solicitacao)
