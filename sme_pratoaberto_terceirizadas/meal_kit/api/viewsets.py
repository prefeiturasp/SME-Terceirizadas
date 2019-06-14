from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.meal_kit.api.serializers import MealKitSerializer, OrderMealKitSerializer, \
    SolicitacaoUnificadaFormularioSerializer, SolicitacaoUnificadaSerializer
from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.users.models import User
from ..models import MealKit, OrderMealKit, SolicitacaoUnificada, SolicitacaoUnificadaFormulario, \
    StatusSolicitacaoUnificada
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
        quantidade_matriculados = 200
        escola = self._valida_escola(request.user)
        if not OrderMealKit.valida_quantidade_matriculados(quantidade_matriculados, int(request.data.get('nro_alunos')),
                                                           request.data.get('evento_data'),
                                                           escola):
            return Response(
                {'error': 'A Quantidade de aluno para o evento, excedeu a quantidade limite de alunos para este dia'},
                status=status.HTTP_400_BAD_REQUEST)
        if not OrderMealKit.valida_duplicidade(request.data, escola):
            return Response({'error': 'Solicitação já cadastrada no sistema com esta data'},
                            status=status.HTTP_400_BAD_REQUEST)
        if OrderMealKit.solicitar_kit_lanche(request.data, escola, request.user):
            return Response({'success': 'Sua solicitação foi enviada com sucesso'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Erro ao tentar salvar solicitação, tente novamente'},
                        status=status.HTTP_502_BAD_GATEWAY)

    def _valida_escola(self, user: User):
        escola = Escola.objects.filter(users=user).first()
        if not escola:
            return Response({'error': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)
        return escola

    @action(detail=False, methods=['post'])
    def solicitacoes(self, request):
        if 'ids' in request.data:
            resposta = OrderMealKit.solicita_kit_lanche_em_lote(request.data, request.user)
            return Response({'success': '{} solicitações enviada com sucesso.'.format(resposta)})
        return Response({'error': 'Ocorreu um error na solicitação em massa, tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def salvar(self, request):
        params = request.data
        escola = Escola.objects.filter(users=request.user).first()
        if not valida_usuario_escola(request.user):
            return Response({'error': 'Sem escola relacinada a este usuário'}, status=status.HTTP_401_UNAUTHORIZED)

        if OrderMealKit.ja_existe_salvo(params, escola) and not params.get('id', None):
            return Response({'error': 'Já existe um evento cadastrado para esta data'},
                            status=status.HTTP_400_BAD_REQUEST)
        OrderMealKit.salvar_solicitacao(params, escola)
        return Response({'success': 'Solicitação salva com sucesso'})


class SolicitacaoUnificadaFormularioViewSet(ModelViewSet):
    """ Endpoint para Formularios de Solicitações Unificadas de Kit Lanches """
    serializer_class = SolicitacaoUnificadaFormularioSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return SolicitacaoUnificadaFormulario.objects.filter(criado_por=self.request.user,
                                                             solicitacaounificada__isnull=True)

    def destroy(self, request, *args, **kwargs):
        response = super(SolicitacaoUnificadaFormularioViewSet, self).destroy(request, *args, **kwargs)
        if response.status_code == 204:
            return Response({'success': 'Solicitação removida com sucesso.'})
        return Response({'error': 'Solicitação não encontrada'}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=['post'])
    def salvar(self, request):
        params = request.data
        usuario = request.user
        escolas = SolicitacaoUnificadaFormulario.existe_solicitacao_para_alguma_escola(request.data)
        if escolas and not params.get('prosseguir', False):
            return Response(
                {'error': 'Já existe um evento cadastrado para alguma(s) escola(s) no dia ' + params.get('dia'),
                 'escolas': escolas},
                status=status.HTTP_400_BAD_REQUEST)
        formulario = SolicitacaoUnificadaFormulario.salvar_formulario(params, usuario)
        if params.get('status') == StatusSolicitacaoUnificada.TO_APPROVE:
            SolicitacaoUnificada.criar_solicitacoes(formulario)
        return Response({'success': 'Solicitação salva com sucesso'}, status=status.HTTP_200_OK)


class SolicitacaoUnificadaViewSet(ModelViewSet):
    """ Endpoint para Solicitações Unificadas de Kit Lanches """
    serializer_class = SolicitacaoUnificadaSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return SolicitacaoUnificada.objects.all()
