
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.fluxo_status import CronogramaWorkflow
from sme_terceirizadas.dados_comuns.permissions import (
    PermissaoParaCadastrarLaboratorio,
    PermissaoParaCadastrarVisualizarEmbalagem,
    PermissaoParaConfirmarCronograma,
    PermissaoParaCriarCronograma,
    PermissaoParaVisualizarCronograma,
    ViewSetActionPermissionMixin
)
from sme_terceirizadas.pre_recebimento.api.filters import CronogramaFilter
from sme_terceirizadas.pre_recebimento.api.paginations import CronogramaPagination
from sme_terceirizadas.pre_recebimento.api.serializers.serializer_create import (
    CronogramaCreateSerializer,
    EmbalagemQldCreateSerializer,
    LaboratorioCreateSerializer,
    SolicitacaoDeAlteracaoCronogramaCreateSerializer
)
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import (
    CronogramaRascunhosSerializer,
    CronogramaSerializer,
    EmbalagemQldSerializer,
    LaboratorioSerializer
)
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    SolicitacaoAlteracaoCronograma
)


class CronogramaModelViewSet(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Cronograma.objects.all()
    serializer_class = CronogramaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CronogramaFilter
    pagination_class = CronogramaPagination
    permission_classes = (PermissaoParaVisualizarCronograma,)
    permission_action_classes = {
        'create': [PermissaoParaCriarCronograma],
        'delete': [PermissaoParaCriarCronograma]
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CronogramaSerializer
        else:
            return CronogramaCreateSerializer

    def get_queryset(self):
        return Cronograma.objects.all().order_by('-criado_em')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by('-alterado_em').distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(
                serializer.data
            )
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='opcoes-etapas')
    def etapas(self, _):
        return Response(EtapasDoCronograma.etapas_to_json())

    @action(detail=False, methods=['GET'], url_path='rascunhos')
    def rascunhos(self, _):
        queryset = self.get_queryset().filter(status__in=[CronogramaWorkflow.RASCUNHO])
        response = {'results': CronogramaRascunhosSerializer(queryset, many=True).data}
        return Response(response)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaConfirmarCronograma,),
            methods=['patch'], url_path='fornecedor-confirma-cronograma')
    def fornecedor_confirma(self, request, uuid=None):
        usuario = request.user

        try:
            cronograma = Cronograma.objects.get(uuid=uuid)
            cronograma.fornecedor_confirma(user=usuario, )
            serializer = CronogramaSerializer(cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Cronograma informado não é valido: {e}'), status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)


class LaboratorioModelViewSet(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Laboratorio.objects.all()
    serializer_class = LaboratorioSerializer
    permission_classes = (PermissaoParaCadastrarLaboratorio,)
    permission_action_classes = {
        'create': [PermissaoParaCadastrarLaboratorio],
        'delete': [PermissaoParaCadastrarLaboratorio]
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return LaboratorioSerializer
        else:
            return LaboratorioCreateSerializer

    @action(detail=False, methods=['GET'], url_path='lista-laboratorios')
    def lista_nomes_laboratorios(self, request):
        queryset = Laboratorio.objects.all()
        response = {'results': [q.nome for q in queryset]}
        return Response(response)


class EmbalagemQldModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = EmbalagemQld.objects.all()
    serializer_class = EmbalagemQldSerializer
    permission_classes = (PermissaoParaCadastrarVisualizarEmbalagem,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return EmbalagemQldSerializer
        else:
            return EmbalagemQldCreateSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes-embalagens')
    def lista_nomes_embalagens(self, request):
        queryset = EmbalagemQld.objects.all().values_list('nome', flat=True)
        response = {'results': queryset}
        return Response(response)


class SolicitacaoDeAlteracaoCronogramaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoAlteracaoCronograma.objects.all()
    serializer_class = SolicitacaoDeAlteracaoCronogramaCreateSerializer
