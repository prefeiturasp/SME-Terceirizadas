from datetime import datetime
from itertools import chain

from django.db import transaction
from django.db.models import CharField, Count, F, Prefetch, Q, QuerySet
from django.db.models.functions import Cast, Substr
from django_filters import rest_framework as filters
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import HomologacaoProdutoWorkflow, ReclamacaoProdutoWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...dados_comuns.permissions import PermissaoParaReclamarDeProduto, UsuarioCODAEGestaoProduto, UsuarioTerceirizada
from ...dados_comuns.utils import url_configs
from ...dieta_especial.models import Alimento
from ...escola.models import Escola
from ...relatorios.relatorios import (
    relatorio_marcas_por_produto_homologacao,
    relatorio_produto_analise_sensorial,
    relatorio_produto_analise_sensorial_recebimento,
    relatorio_produto_homologacao,
    relatorio_produtos_agrupado_terceirizada,
    relatorio_produtos_em_analise_sensorial,
    relatorio_produtos_situacao,
    relatorio_produtos_suspensos,
    relatorio_reclamacao
)
from ...terceirizada.api.serializers.serializers import TerceirizadaSimplesSerializer
from ...terceirizada.models import Edital
from ..constants import (
    AVALIAR_RECLAMACAO_HOMOLOGACOES_STATUS,
    AVALIAR_RECLAMACAO_RECLAMACOES_STATUS,
    NOVA_RECLAMACAO_HOMOLOGACOES_STATUS,
    RESPONDER_RECLAMACAO_HOMOLOGACOES_STATUS,
    RESPONDER_RECLAMACAO_RECLAMACOES_STATUS
)
from ..forms import ProdutoJaExisteForm, ProdutoPorParametrosForm
from ..models import (
    AnaliseSensorial,
    EmbalagemProduto,
    Fabricante,
    HomologacaoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    ItemCadastro,
    Marca,
    NomeDeProdutoEdital,
    Produto,
    ProdutoEdital,
    ProtocoloDeDietaEspecial,
    ReclamacaoDeProduto,
    RespostaAnaliseSensorial,
    SolicitacaoCadastroProdutoDieta,
    UnidadeMedida
)
from ..utils import (
    CadastroProdutosEditalPagination,
    ItemCadastroPagination,
    StandardResultsSetPagination,
    agrupa_por_terceirizada,
    converte_para_datetime,
    cria_filtro_aditivos,
    cria_filtro_produto_por_parametros_form,
    get_filtros_data
)
from .filters import CadastroProdutosEditalFilter, ItemCadastroFilter, ProdutoFilter, filtros_produto_reclamacoes
from .serializers.serializers import (
    CadastroProdutosEditalSerializer,
    EmbalagemProdutoSerialzer,
    FabricanteSerializer,
    FabricanteSimplesSerializer,
    HomologacaoProdutoPainelGerencialSerializer,
    HomologacaoProdutoSerializer,
    ImagemDoProdutoSerializer,
    InformacaoNutricionalSerializer,
    ItensCadastroCreateSerializer,
    ItensCadastroSerializer,
    MarcaSerializer,
    MarcaSimplesSerializer,
    NomeDeProdutoEditalSerializer,
    ProdutoEditalSerializer,
    ProdutoHomologadosPorParametrosSerializer,
    ProdutoListagemSerializer,
    ProdutoReclamacaoSerializer,
    ProdutoRelatorioAnaliseSensorialSerializer,
    ProdutoRelatorioSituacaoSerializer,
    ProdutoSerializer,
    ProdutoSimplesSerializer,
    ProdutoSuspensoSerializer,
    ProtocoloDeDietaEspecialSerializer,
    ProtocoloSimplesSerializer,
    ReclamacaoDeProdutoSerializer,
    ReclamacaoDeProdutoSimplesSerializer,
    SolicitacaoCadastroProdutoDietaSerializer,
    SubstitutosSerializer,
    UnidadeMedidaSerialzer
)
from .serializers.serializers_create import (
    CadastroProdutosEditalCreateSerializer,
    ProdutoEditalCreateSerializer,
    ProdutoSerializerCreate,
    ReclamacaoDeProdutoSerializerCreate,
    RespostaAnaliseSensorialSearilzerCreate,
    SolicitacaoCadastroProdutoDietaSerializerCreate
)

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'count': self.page.paginator.count,
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })


class ListaNomesUnicos():
    @action(detail=False, methods=['GET'], url_path='lista-nomes-unicos')
    def lista_nomes_unicos(self, request):
        query_set = self.filter_queryset(self.get_queryset()).values('nome').distinct()
        nomes_unicos = [i['nome'] for i in query_set]
        return Response({
            'results': nomes_unicos,
            'count': len(nomes_unicos)
        })


class InformacaoNutricionalBaseViewSet(viewsets.ReadOnlyModelViewSet):

    def possui_tipo_nutricional_na_lista(self, infos_nutricionais, nome):
        tem_tipo_nutricional = False
        if len(infos_nutricionais) > 0:
            for info_nutricional in infos_nutricionais:
                if info_nutricional['nome'] == nome:
                    tem_tipo_nutricional = True
        return tem_tipo_nutricional

    def adiciona_informacao_em_tipo_nutricional(self, infos_nutricionais, objeto):
        tipo_nutricional = objeto.tipo_nutricional.nome
        for item in infos_nutricionais:
            if item['nome'] == tipo_nutricional:
                item['informacoes_nutricionais'].append({
                    'nome': objeto.nome,
                    'uuid': objeto.uuid,
                    'medida': objeto.medida
                })
        return infos_nutricionais

    def _agrupa_informacoes_por_tipo(self, query_set):
        infos_nutricionais = []
        for objeto in query_set:
            tipo_nutricional = objeto.tipo_nutricional.nome
            if self.possui_tipo_nutricional_na_lista(infos_nutricionais, tipo_nutricional):
                infos_nutricionais = self.adiciona_informacao_em_tipo_nutricional(
                    infos_nutricionais, objeto)
            else:
                info_nutricional = {
                    'nome': tipo_nutricional,
                    'informacoes_nutricionais': [{
                        'nome': objeto.nome,
                        'uuid': objeto.uuid,
                        'medida': objeto.medida
                    }]
                }
                infos_nutricionais.append(info_nutricional)
        return infos_nutricionais


class ImagensViewset(mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    lookup_field = 'uuid'
    queryset = ImagemDoProduto.objects.all()
    serializer_class = ImagemDoProdutoSerializer


class HomologacaoProdutoPainelGerencialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = HomologacaoProdutoPainelGerencialSerializer
    queryset = HomologacaoProduto.objects.all()
    pagination_class = CustomPagination

    def get_lista_status(self):
        lista_status = [
            HomologacaoProduto.workflow_class.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            HomologacaoProduto.workflow_class.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            HomologacaoProduto.workflow_class.CODAE_PEDIU_ANALISE_RECLAMACAO,
            HomologacaoProduto.workflow_class.CODAE_AUTORIZOU_RECLAMACAO,
            HomologacaoProduto.workflow_class.CODAE_SUSPENDEU,
            HomologacaoProduto.workflow_class.CODAE_HOMOLOGADO,
            HomologacaoProduto.workflow_class.CODAE_NAO_HOMOLOGADO,
            HomologacaoProduto.workflow_class.TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_UE,
            HomologacaoProduto.workflow_class.UE_RESPONDEU_QUESTIONAMENTO,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProduto.workflow_class.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO]
        if self.request.user.tipo_usuario in [constants.TIPO_USUARIO_TERCEIRIZADA,
                                              constants.TIPO_USUARIO_GESTAO_PRODUTO]:
            lista_status.append(
                HomologacaoProduto.workflow_class.CODAE_QUESTIONADO)

            lista_status.append(
                HomologacaoProduto.workflow_class.CODAE_PEDIU_ANALISE_SENSORIAL)

            lista_status.append(
                HomologacaoProduto.workflow_class.CODAE_PENDENTE_HOMOLOGACAO)

        return lista_status

    def reclamacoes_por_usuario(self, workflow, raw_sql, data, query_set):  # noqa C901
        if (workflow in [
            HomologacaoProduto.workflow_class.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONADO] and
                self.request.user.tipo_usuario == constants.TIPO_USUARIO_TERCEIRIZADA):
            if query_set is not None:
                query_set = query_set.filter(rastro_terceirizada=self.request.user.vinculo_atual.instituicao)
            else:
                data['terceirizada'] = self.request.user.vinculo_atual.object_id
                raw_sql += "AND %(homologacoes_produto)s.rastro_terceirizada_id = '%(terceirizada)s' "
        elif (workflow in [
            HomologacaoProduto.workflow_class.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            HomologacaoProduto.workflow_class.CODAE_PEDIU_ANALISE_RECLAMACAO,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_UE,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProduto.workflow_class.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            HomologacaoProduto.workflow_class.UE_RESPONDEU_QUESTIONAMENTO,
            HomologacaoProduto.workflow_class.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO] and
                self.request.user.tipo_usuario == constants.TIPO_USUARIO_ESCOLA):
            if query_set is not None:
                query_set = query_set.filter(reclamacoes__escola=self.request.user.vinculo_atual.instituicao)
            else:
                data['escola'] = self.request.user.vinculo_atual.object_id
                raw_sql += "AND %(reclamacoes_produto)s.escola_id = '%(escola)s' "
        elif (workflow in [
            HomologacaoProduto.workflow_class.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            HomologacaoProduto.workflow_class.CODAE_PEDIU_ANALISE_RECLAMACAO,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_UE,
            HomologacaoProduto.workflow_class.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProduto.workflow_class.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            HomologacaoProduto.workflow_class.UE_RESPONDEU_QUESTIONAMENTO,
            HomologacaoProduto.workflow_class.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO] and
                self.request.user.tipo_usuario == constants.TIPO_USUARIO_NUTRISUPERVISOR):
            if query_set is not None:
                query_set = query_set.filter(
                    reclamacoes__reclamante_registro_funcional=self.request.user.registro_funcional)
            else:
                data['registro_funcional'] = self.request.user.registro_funcional
                raw_sql += "AND %(reclamacoes_produto)s.reclamante_registro_funcional = '%(registro_funcional)s' "
        return query_set

    def dados_dashboard(self, query_set: QuerySet, use_raw=True) -> list:
        sumario = []

        for workflow in self.get_lista_status():
            if use_raw:
                data = {'logs': LogSolicitacoesUsuario._meta.db_table,
                        'homologacao_produto': HomologacaoProduto._meta.db_table,
                        'reclamacoes_produto': ReclamacaoDeProduto._meta.db_table,
                        'status': workflow}
                raw_sql = ('SELECT %(homologacao_produto)s.* FROM %(homologacao_produto)s '
                           'JOIN (SELECT uuid_original, MAX(criado_em) AS log_criado_em FROM %(logs)s '
                           'GROUP BY uuid_original) '
                           'AS most_recent_log '
                           'ON %(homologacao_produto)s.uuid = most_recent_log.uuid_original '
                           'LEFT JOIN (SELECT DISTINCT ON (homologacao_produto_id) homologacao_produto_id, escola_id '
                           'AS escola_reclamacao_id FROM %(reclamacoes_produto)s) AS homolog_com_reclamacao '
                           'ON homolog_com_reclamacao.homologacao_produto_id = %(homologacao_produto)s.id '
                           "WHERE %(homologacao_produto)s.status = '%(status)s' ")
                self.reclamacoes_por_usuario(workflow, raw_sql, data, None)
                raw_sql += 'ORDER BY log_criado_em DESC'
                qs = query_set.raw(raw_sql % data)
            else:
                qs = self.reclamacoes_por_usuario(workflow, None, None, query_set)
                qs = sorted(qs.filter(status=workflow).distinct().all(),
                            key=lambda x: x.ultimo_log.criado_em if x.ultimo_log else '-criado_em', reverse=True)
            sumario.append({
                'status': workflow,
                'dados': self.get_serializer(
                    qs[:6],
                    context={'request': self.request}, many=True).data
            })

        return sumario

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard(self, request):
        query_set = self.get_queryset()
        use_raw = self.request.user.tipo_usuario not in [constants.TIPO_USUARIO_ESCOLA,
                                                         constants.TIPO_USUARIO_NUTRISUPERVISOR]
        response = {'results': self.dados_dashboard(query_set=query_set, use_raw=use_raw)}
        return Response(response)

    @action(detail=False, methods=['POST'], url_path='filtro-homologacoes-por-titulo-marca')
    def solicitacoes_homologacao_por_titulo_marca(self, request):
        query_set = self.get_queryset()
        titulo = request.data.get('titulo_produto',)
        marca = request.data.get('marca_produto',)

        if (titulo):
            query_set = query_set.annotate(id_amigavel=Substr(Cast(F('uuid'), output_field=CharField()), 1, 5)).filter(
                Q(id_amigavel__icontains=titulo) |
                Q(produto__nome__icontains=titulo))
        if (marca):
            query_set = query_set.filter(produto__marca__nome__icontains=marca)

        response = {'results': self.dados_dashboard(query_set=query_set, use_raw=False)}
        return Response(response)

    @action(detail=False,  # noqa C901
            methods=['GET', 'POST'],
            url_path=f'filtro-por-status/{constants.FILTRO_STATUS_HOMOLOGACAO}')
    def solicitacoes_homologacao_por_status(self, request, filtro_aplicado=constants.RASCUNHO):
        filtros = {}
        user = self.request.user
        page = request.GET.get('page', False)
        titulo = request.data.get('titulo_produto',)
        query_set = self.get_queryset()

        data = {'logs': LogSolicitacoesUsuario._meta.db_table,
                'homologacao_produto': HomologacaoProduto._meta.db_table,
                'reclamacoes_produto': ReclamacaoDeProduto._meta.db_table}

        raw_sql = ('SELECT %(homologacao_produto)s.* FROM %(homologacao_produto)s '
                   'JOIN (SELECT uuid_original, MAX(criado_em) AS log_criado_em FROM %(logs)s '
                   'GROUP BY uuid_original) '
                   'AS most_recent_log '
                   'ON %(homologacao_produto)s.uuid = most_recent_log.uuid_original '
                   'LEFT JOIN (SELECT DISTINCT ON (homologacao_produto_id) homologacao_produto_id, escola_id '
                   'AS escola_reclamacao_id FROM %(reclamacoes_produto)s) AS homolog_com_reclamacao '
                   'ON homolog_com_reclamacao.homologacao_produto_id = %(homologacao_produto)s.id ')
        if filtro_aplicado:
            if filtro_aplicado == 'codae_pediu_analise_reclamacao':
                status__in = ['ESCOLA_OU_NUTRICIONISTA_RECLAMOU',
                              'CODAE_PEDIU_ANALISE_RECLAMACAO',
                              'CODAE_QUESTIONOU_UE']
                common_status = ("WHERE (%(homologacao_produto)s.status = 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU' "
                                 "OR %(homologacao_produto)s.status = 'CODAE_QUESTIONOU_UE' "
                                 f"OR %(homologacao_produto)s.status = '{filtro_aplicado.upper()}' ")

                if request.user.vinculo_atual.perfil.nome in [constants.COORDENADOR_GESTAO_PRODUTO,
                                                              constants.ADMINISTRADOR_GESTAO_PRODUTO,
                                                              constants.ADMINISTRADOR_TERCEIRIZADA]:
                    status__in.append('TERCEIRIZADA_RESPONDEU_RECLAMACAO')
                    raw_sql += (common_status +
                                "OR %(homologacao_produto)s.status = 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' "
                                "OR %(homologacao_produto)s.status = 'CODAE_QUESTIONOU_NUTRISUPERVISOR' "
                                "OR %(homologacao_produto)s.status = 'NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO') ")
                filtros['status__in'] = status__in

                if request.user.vinculo_atual.perfil.nome == constants.COORDENADOR_SUPERVISAO_NUTRICAO:
                    status__in.append('CODAE_QUESTIONOU_NUTRISUPERVISOR')
                    raw_sql += (common_status +
                                "OR %(homologacao_produto)s.status = 'CODAE_QUESTIONOU_NUTRISUPERVISOR') ")
                filtros['status__in'] = status__in

                if request.user.tipo_usuario == constants.TIPO_USUARIO_ESCOLA:
                    filtros['reclamacoes__escola'] = request.user.vinculo_atual.instituicao
                    if 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' not in status__in:
                        status__in.append('TERCEIRIZADA_RESPONDEU_RECLAMACAO')
                    raw_sql += common_status
                    if 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' not in raw_sql:
                        raw_sql += "OR %(homologacao_produto)s.status = 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' "
                    escola_id = user.vinculo_atual.object_id
                    raw_sql += f') AND escola_reclamacao_id = {escola_id} '

                if 'WHERE' not in raw_sql:
                    raw_sql += common_status + ') '

            elif filtro_aplicado == 'codae_homologado':

                if user.tipo_usuario == constants.TIPO_USUARIO_TERCEIRIZADA:
                    filtros['status__in'] = ['ESCOLA_OU_NUTRICIONISTA_RECLAMOU',
                                             'TERCEIRIZADA_RESPONDEU_RECLAMACAO',
                                             filtro_aplicado.upper()]
                    raw_sql += ("WHERE (%(homologacao_produto)s.status = 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU' "
                                "OR %(homologacao_produto)s.status = 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' "
                                f"OR %(homologacao_produto)s.status = '{filtro_aplicado.upper()}') ")

                elif user.tipo_usuario == constants.TIPO_USUARIO_GESTAO_PRODUTO:
                    filtros['status'] = filtro_aplicado.upper()
                    raw_sql += f"WHERE %(homologacao_produto)s.status = '{filtro_aplicado.upper()}' "

                else:
                    filtros['status__in'] = ['ESCOLA_OU_NUTRICIONISTA_RECLAMOU',
                                             'CODAE_PEDIU_ANALISE_RECLAMACAO',
                                             'TERCEIRIZADA_RESPONDEU_RECLAMACAO',
                                             filtro_aplicado.upper()]
                    raw_sql += ("WHERE (%(homologacao_produto)s.status = 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU' "
                                "OR %(homologacao_produto)s.status = 'CODAE_PEDIU_ANALISE_RECLAMACAO' "
                                "OR %(homologacao_produto)s.status = 'TERCEIRIZADA_RESPONDEU_RECLAMACAO' "
                                f"OR %(homologacao_produto)s.status = '{filtro_aplicado.upper()}') ")
            elif filtro_aplicado == 'codae_nao_homologado':
                status__in = ['CODAE_NAO_HOMOLOGADO',
                              'TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO']
                filtros['status__in'] = status__in
                raw_sql += ("WHERE (%(homologacao_produto)s.status = 'TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO' "
                            f"OR %(homologacao_produto)s.status = '{filtro_aplicado.upper()}') ")
            elif filtro_aplicado == 'codae_suspendeu':
                status__in = ['CODAE_SUSPENDEU',
                              'CODAE_AUTORIZOU_RECLAMACAO']
                filtros['status__in'] = status__in
                raw_sql += ("WHERE (%(homologacao_produto)s.status = 'CODAE_SUSPENDEU' "
                            "OR %(homologacao_produto)s.status = 'CODAE_AUTORIZOU_RECLAMACAO') ")
            else:
                filtros['status'] = filtro_aplicado.upper()
                raw_sql += f"WHERE %(homologacao_produto)s.status = '{filtro_aplicado.upper()}' "

        raw_sql += 'ORDER BY log_criado_em DESC'
        if page:
            query_set = query_set.raw(raw_sql % data)
            page = self.paginate_queryset(query_set)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            if titulo:
                query_set = query_set.annotate(
                    id_amigavel=Substr(Cast(F('uuid'), output_field=CharField()), 1, 5)
                ).filter(Q(id_amigavel__icontains=titulo) | Q(produto__nome__icontains=titulo))
                query_set = sorted(query_set.filter(**filtros).distinct(),
                                   key=lambda x: x.ultimo_log.criado_em if x.ultimo_log else '-criado_em', reverse=True)
            else:
                query_set = sorted(self.get_queryset().filter(**filtros).distinct(),
                                   key=lambda x: x.ultimo_log.criado_em if x.ultimo_log else '-criado_em', reverse=True)
            serializer = self.get_serializer if filtro_aplicado != constants.RASCUNHO else HomologacaoProdutoSerializer
            response = {'results': serializer(
                query_set, context={'request': request}, many=True).data}
            return Response(response)


class HomologacaoProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = HomologacaoProdutoSerializer
    queryset = HomologacaoProduto.objects.all()

    @action(detail=True,  # noqa C901
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_HOMOLOGA)
    def codae_homologa(self, request, uuid=None):
        homologacao_produto = self.get_object()
        uri = reverse(
            'Produtos-relatorio',
            args=[homologacao_produto.produto.uuid]
        )
        editais = request.data.get('editais', [])
        if not editais:
            return Response(dict(detail='É necessario informar algum edital.'),
                            status=HTTP_406_NOT_ACCEPTABLE)
        try:
            homologacao_produto.codae_homologa(
                user=request.user,
                link_pdf=url_configs('API', {'uri': uri}))
            eh_para_alunos_com_dieta = homologacao_produto.produto.eh_para_alunos_com_dieta
            for edital_uuid in editais:
                ProdutoEdital.objects.create(
                    produto=homologacao_produto.produto,
                    edital=Edital.objects.get(uuid=edital_uuid),
                    tipo_produto=ProdutoEdital.DIETA_ESPECIAL if eh_para_alunos_com_dieta else ProdutoEdital.COMUM
                )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_NAO_HOMOLOGA)
    def codae_nao_homologa(self, request, uuid=None):
        homologacao_produto = self.get_object()
        uri = reverse(
            'Produtos-relatorio',
            args=[homologacao_produto.produto.uuid]
        )
        try:
            justificativa = request.data.get('justificativa', '')
            homologacao_produto.codae_nao_homologa(
                user=request.user,
                justificativa=justificativa,
                link_pdf=url_configs('API', {'uri': uri})
            )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona(self, request, uuid=None):
        homologacao_produto = self.get_object()
        uri = reverse(
            'Produtos-relatorio',
            args=[homologacao_produto.produto.uuid]
        )
        try:
            justificativa = request.data.get('justificativa', '')
            homologacao_produto.codae_questiona(
                user=request.user,
                justificativa=justificativa,
                link_pdf=url_configs('API', {'uri': uri})
            )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,  # noqa C901
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_PEDE_ANALISE_SENSORIAL)
    def codae_pede_analise_sensorial(self, request, uuid=None):
        from sme_terceirizadas.produto.models import AnaliseSensorial
        from sme_terceirizadas.terceirizada.models import Terceirizada
        homologacao_produto = self.get_object()
        uri = reverse(
            'Produtos-relatorio',
            args=[homologacao_produto.produto.uuid]
        )
        try:
            justificativa = request.data.get('justificativa', '')
            terceirizada_uuid = request.data.get('uuidTerceirizada', '')
            if not terceirizada_uuid:
                return Response({'detail': 'O uuid da terceirizada é obrigatório'})

            terceirizada = Terceirizada.objects.filter(uuid=terceirizada_uuid).first()
            if not terceirizada:
                return Response({'detail': f'Terceirizada para uuid {terceirizada_uuid} não encontrado.'})

            AnaliseSensorial.objects.create(
                homologacao_produto=homologacao_produto,
                terceirizada=terceirizada)

            homologacao_produto.gera_protocolo_analise_sensorial()
            homologacao_produto.codae_pede_analise_sensorial(
                user=request.user, justificativa=justificativa,
                link_pdf=url_configs('API', {'uri': uri})
            )

            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,  # noqa C901
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_CANCELA_ANALISE_SENSORIAL)
    def codae_cancela_analise_sensorial(self, request, uuid=None):
        from sme_terceirizadas.produto.models import AnaliseSensorial
        homologacao_produto = self.get_object()
        _status = LogSolicitacoesUsuario.STATUS_POSSIVEIS
        status = {v: k for (k, v) in _status}
        try:
            justificativa = request.data.get('justificativa', '')
            logs = homologacao_produto.logs
            log_anterior_pedido_analise = logs[logs.count() - 2]
            homologacao_produto.codae_cancela_analise_sensorial(
                user=request.user, justificativa=justificativa,
            )

            if log_anterior_pedido_analise.status_evento == status['Escola/Nutricionista reclamou do produto']:
                homologacao_produto.escola_ou_nutricionista_reclamou(
                    user=log_anterior_pedido_analise.usuario,
                    reclamacao={'reclamacao': log_anterior_pedido_analise.justificativa},
                    nao_enviar_email=True
                )
                ultima_reclamacao = homologacao_produto.reclamacoes.last()
                ultima_reclamacao.codae_cancela_analise_sensorial(
                    user=log_anterior_pedido_analise.usuario,
                    anexos=ultima_reclamacao.anexos.all(),
                    justificativa=ultima_reclamacao.reclamacao
                )
            elif log_anterior_pedido_analise.status_evento == status['Solicitação Realizada']:
                homologacao_produto.inicia_fluxo(user=log_anterior_pedido_analise.usuario)
            elif log_anterior_pedido_analise.status_evento == status['CODAE homologou']:
                homologacao_produto.codae_homologa(
                    user=log_anterior_pedido_analise.usuario,
                    anexos=log_anterior_pedido_analise.anexos.all(),
                    justificativa=log_anterior_pedido_analise.justificativa,
                    nao_enviar_email=True
                )

            homologacao_produto.protocolo_analise_sensorial = ''
            uuid_ultima_analise = homologacao_produto.ultima_analise.uuid
            AnaliseSensorial.objects.get(uuid=uuid_ultima_analise).delete()
            homologacao_produto.save()

            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,  # noqa C901
            permission_classes=[PermissaoParaReclamarDeProduto],
            methods=['patch'],
            url_path=constants.ESCOLA_OU_NUTRI_RECLAMA)
    def escola_ou_nutricodae_reclama(self, request, uuid=None):
        homologacao_produto = self.get_object()
        data = request.data.copy()
        data['homologacao_produto'] = homologacao_produto.id
        data['criado_por'] = request.user.id
        try:
            serializer_reclamacao = ReclamacaoDeProdutoSerializerCreate(
                data=data)
            if not serializer_reclamacao.is_valid():
                return Response(serializer_reclamacao.errors)
            serializer_reclamacao.save()
            if homologacao_produto.status == HomologacaoProduto.workflow_class.CODAE_HOMOLOGADO:
                homologacao_produto.escola_ou_nutricionista_reclamou(
                    user=request.user,
                    reclamacao=serializer_reclamacao.data)
            return Response(serializer_reclamacao.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_PEDE_ANALISE_RECLAMACAO)
    def codae_pede_analise_reclamacao(self, request, uuid=None):
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_pediu_analise_reclamacao(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_ACEITA_RECLAMACAO)
    def codae_aceita_reclamacao(self, request, uuid=None):
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_autorizou_reclamacao(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa,
                nao_enviar_email=True
            )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_RECUSA_RECLAMACAO)
    def codae_recusa_reclamacao(self, request, uuid=None):
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_homologa(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa,
                nao_enviar_email=True
            )
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.SUSPENDER_PRODUTO)
    def suspender(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_suspende(request=request)
            return Response('Homologação suspensa')
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.ATIVAR_PRODUTO)
    def ativar(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_ativa(request=request)
            return Response('Homologação ativada')
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioTerceirizada],
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_RESPONDE_RECLAMACAO)
    def terceirizada_responde_reclamacao(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.terceirizada_responde_reclamacao(
                request=request)
            return Response('Reclamação respondida')
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_path='reclamacao')
    def reclamacao_homologao(self, request, uuid=None):
        homologacao_produto = self.get_object()
        reclamacao = homologacao_produto.reclamacoes.filter(
            status=ReclamacaoProdutoWorkflow.CODAE_ACEITOU).first()
        serializer = ReclamacaoDeProdutoSimplesSerializer(reclamacao)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='numero_protocolo')
    def numero_relatorio_analise_sensorial(self, request):
        homologacao = HomologacaoProduto()
        protocolo = homologacao.retorna_numero_do_protocolo()
        return Response(protocolo)

    def retorna_datetime(self, data):
        data = datetime.strptime(data, '%d/%m/%Y')
        return data

    @action(detail=True,
            permission_classes=[UsuarioTerceirizada],
            methods=['post'],
            url_path=constants.GERAR_PDF)
    def gerar_pdf_homologacao(self, request, uuid=None):
        homologacao_produto = self.get_object()
        homologacao_produto.pdf_gerado = True
        homologacao_produto.save()
        return Response('PDF Homologação gerado')

    @action(detail=False,
            permission_classes=[UsuarioTerceirizada],
            methods=['get'],
            url_path=constants.AGUARDANDO_ANALISE_SENSORIAL)
    def homolocoes_aguardando_analise_sensorial(self, request):
        homologacoes = HomologacaoProduto.objects.filter(
            status=HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_SENSORIAL
        )
        serializer = self.get_serializer(homologacoes, many=True)
        return Response(serializer.data)

    @action(detail=True,
            permission_classes=[UsuarioTerceirizada],
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO)
    def terceirizada_cancelou_solicitacao_homologacao(self, request, uuid=None):
        homologacao_produto = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            homologacao_produto.terceirizada_cancelou_solicitacao_homologacao(
                user=request.user, justificativa=justificativa)
            return Response('Cancelamento de solicitação de homologação realizada com sucesso!')
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        homologacao_produto = self.get_object()
        if homologacao_produto.pode_excluir:
            homologacao_produto.produto.delete()
            homologacao_produto.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(dict(detail='Você só pode excluir quando o status for RASCUNHO.'),
                            status=status.HTTP_403_FORBIDDEN)


class ProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProdutoSerializer
    queryset = Produto.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProdutoFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).select_related(
            'marca', 'fabricante').order_by('criado_em')
        if isinstance(request.user.vinculo_atual.instituicao, Escola):
            contratos = request.user.vinculo_atual.instituicao.lote.contratos_do_lote.all()
            editais = contratos.values_list('edital', flat=True)
            queryset = queryset.filter(vinculos__edital__in=editais)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProdutoListagemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProdutoListagemSerializer(queryset, many=True)
        return Response(serializer.data)

    def paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, context={'request': self.request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_paginated_response(
            queryset, context={'request': self.request}, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):  # noqa C901
        if self.action in ['create', 'update', 'partial_update']:
            return ProdutoSerializerCreate
        if self.action == 'filtro_relatorio_em_analise_sensorial':
            return ProdutoRelatorioAnaliseSensorialSerializer
        if self.action == 'filtro_relatorio_situacao_produto':
            return ProdutoRelatorioSituacaoSerializer
        if self.action == 'filtro_homologados_por_parametros':
            return ProdutoHomologadosPorParametrosSerializer
        if self.action == 'filtro_relatorio_produto_suspenso':
            return ProdutoSuspensoSerializer
        if self.action in ['filtro_reclamacoes', 'filtro_reclamacoes_terceirizada',
                           'filtro_avaliar_reclamacoes']:
            return ProdutoReclamacaoSerializer
        return ProdutoSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_produtos(self, request):
        query_set = Produto.objects.filter(ativo=True)
        filtrar_por = request.query_params.get('filtrar_por', None)
        if filtrar_por == 'reclamacoes/':
            query_set = query_set.filter(
                homologacao__reclamacoes__isnull=False,
                homologacao__status__in=[
                    'CODAE_PEDIU_ANALISE_RECLAMACAO',
                    'TERCEIRIZADA_RESPONDEU_RECLAMACAO',
                    'ESCOLA_OU_NUTRICIONISTA_RECLAMOU'
                ]
            )
        response = {'results': ProdutoSimplesSerializer(
            query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-unicos')
    def lista_nomes_unicos(self, request):
        query_set = self.filter_queryset(self.get_queryset()).filter(ativo=True).values('nome').distinct()
        nomes_unicos = [p['nome'] for p in query_set]
        return Response({
            'results': nomes_unicos,
            'count': len(nomes_unicos)
        })

    @action(detail=False, methods=['GET'], url_path='lista-nomes-nova-reclamacao')
    def lista_produtos_nova_reclamacao(self, request):
        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status__in=NOVA_RECLAMACAO_HOMOLOGACOES_STATUS
        ).only('nome').values('nome').order_by('nome').distinct()
        response = {'results': [{'uuid': 'uuid', 'nome': r['nome']} for r in query_set]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-avaliar-reclamacao')
    def lista_produtos_avaliar_reclamacao(self, request):
        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status__in=AVALIAR_RECLAMACAO_HOMOLOGACOES_STATUS,
            homologacao__reclamacoes__status__in=AVALIAR_RECLAMACAO_RECLAMACOES_STATUS
        ).only('nome').values('nome').order_by('nome').distinct()
        response = {'results': [{'uuid': 'uuid', 'nome': r['nome']} for r in query_set]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao')
    def lista_produtos_responder_reclamacao(self, request):
        user = request.user
        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status__in=RESPONDER_RECLAMACAO_HOMOLOGACOES_STATUS,
            homologacao__reclamacoes__status__in=RESPONDER_RECLAMACAO_RECLAMACOES_STATUS,
            homologacao__rastro_terceirizada=user.vinculo_atual.instituicao
        ).only('nome').values('nome').order_by('nome').distinct()
        response = {'results': [{'uuid': 'uuid', 'nome': r['nome']} for r in query_set]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-escola')
    def lista_produtos_responder_reclamacao_escola(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE,
            HomologacaoProdutoWorkflow.UE_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE]

        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status__in=status_homologacoes,
            homologacao__reclamacoes__status__in=status_reclamacoes,
            homologacao__reclamacoes__escola=user.vinculo_atual.instituicao
        ).only('nome').values('nome').order_by('nome').distinct()
        response = {'results': [{'uuid': 'uuid', 'nome': r['nome']} for r in query_set]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-nutrisupervisor')
    def lista_produtos_responder_reclamacao_nutrisupervisor(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProdutoWorkflow.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [
            ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
            ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR]

        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status__in=status_homologacoes,
            homologacao__reclamacoes__status__in=status_reclamacoes,
            homologacao__reclamacoes__reclamante_registro_funcional=user.registro_funcional
        ).only('nome').values('nome').order_by('nome').distinct()
        response = {'results': [{'uuid': 'uuid', 'nome': r['nome']} for r in query_set]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-homologados')
    def lista_produtos_homologados(self, request):
        status = 'CODAE_HOMOLOGADO'
        query_set = Produto.objects.filter(
            ativo=True,
            homologacao__status=status
        )
        response = {
            'results': ProdutoSimplesSerializer(query_set, many=True).data
        }
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-substitutos')
    def lista_substitutos(self, request):
        # Retorna todos os alimentos + os produtos homologados.
        status = 'CODAE_HOMOLOGADO'
        alimentos = Alimento.objects.filter(tipo='E')
        produtos = Produto.objects.filter(ativo=True, homologacao__status=status)
        alimentos.model = Produto
        query_set = list(chain(alimentos, produtos))
        response = {
            'results': SubstitutosSerializer(query_set, many=True).data
        }
        return Response(response)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-nome/(?P<produto_nome>[^/.]+)')
    def filtro_por_nome(self, request, produto_nome=None):
        query_set = Produto.filtrar_por_nome(nome=produto_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-fabricante/(?P<fabricante_nome>[^/.]+)')
    def filtro_por_fabricante(self, request, fabricante_nome=None):
        query_set = Produto.filtrar_por_fabricante(nome=fabricante_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-marca/(?P<marca_nome>[^/.]+)')
    def filtro_por_marca(self, request, marca_nome=None):
        query_set = Produto.filtrar_por_marca(nome=marca_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            url_path='todos-produtos')
    def filtro_consolidado(self, request):
        query_set = Produto.objects.all()
        response = {'results': self.get_serializer(query_set, many=True).data}
        return Response(response)

    @action(detail=True, url_path=constants.RELATORIO,
            methods=['get'], permission_classes=(AllowAny,))
    def relatorio(self, request, uuid=None):
        return relatorio_produto_homologacao(request, produto=self.get_object())

    @action(detail=False,
            methods=['GET'],
            permission_classes=(AllowAny,),
            url_path='marcas-por-produto')
    def relatorio_marcas_por_produto(self, request):
        form = ProdutoPorParametrosForm(request.GET)

        if not form.is_valid():
            return Response(form.errors)

        return relatorio_marcas_por_produto_homologacao(
            request,
            produtos=self.get_queryset_filtrado_agrupado(request, form),
            filtros=form.cleaned_data
        )

    @action(detail=True, url_path=constants.RELATORIO_ANALISE,
            methods=['get'], permission_classes=(IsAuthenticated,))
    def relatorio_analise_sensorial(self, request, uuid=None):
        return relatorio_produto_analise_sensorial(request, produto=self.get_object())

    @action(detail=True, url_path=constants.RELATORIO_RECEBIMENTO,
            methods=['get'], permission_classes=(IsAuthenticated,))
    def relatorio_analise_sensorial_recebimento(self, request, uuid=None):
        return relatorio_produto_analise_sensorial_recebimento(request, produto=self.get_object())

    def get_queryset_filtrado(self, cleaned_data):
        campos_a_pesquisar = cria_filtro_produto_por_parametros_form(cleaned_data)
        if 'aditivos' in cleaned_data:
            filtro_aditivos = cria_filtro_aditivos(cleaned_data['aditivos'])
            return self.get_queryset().filter(**campos_a_pesquisar).filter(filtro_aditivos).exclude(homologacao=None)
        else:
            return self.get_queryset().filter(**campos_a_pesquisar).exclude(homologacao=None)

    @action(detail=False,
            methods=['POST'],
            url_path='filtro-por-parametros')
    def filtro_por_parametros(self, request):
        form = ProdutoPorParametrosForm(request.data)

        if not form.is_valid():
            return Response(form.errors)

        queryset = self.get_queryset_filtrado(form.cleaned_data)
        return self.paginated_response(queryset.order_by('criado_em'))

    def serializa_agrupamento(self, agrupamento):
        serializado = []

        for grupo in agrupamento['results']:
            serializado.append({
                'terceirizada': TerceirizadaSimplesSerializer(grupo['terceirizada']).data,
                'produtos': [
                    self.get_serializer(prod, context={'request': self.request}).data for prod in grupo['produtos']
                ]
            })

        return serializado

    @action(detail=False,
            methods=['POST'],
            url_path='filtro-por-parametros-agrupado-terceirizada')
    def filtro_por_parametros_agrupado_terceirizada(self, request):
        form = ProdutoPorParametrosForm(request.data)

        if not form.is_valid():
            return Response(form.errors)

        form_data = form.cleaned_data.copy()
        form_data['status'] = [
            HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
            HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU
        ]

        queryset = self.get_queryset_filtrado(form_data)
        queryset.order_by('criado_por')

        dados_agrupados = agrupa_por_terceirizada(queryset)

        return Response(self.serializa_agrupamento(dados_agrupados))

    def get_queryset_filtrado_agrupado(self, request, form):
        form_data = form.cleaned_data.copy()
        form_data['status'] = [
            HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
            HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU
        ]

        queryset = self.get_queryset_filtrado(form_data)
        queryset.order_by('criado_por')

        produtos = queryset.values_list('nome', 'marca__nome').order_by('nome', 'marca__nome')
        produtos_e_marcas = {}
        for key, value in produtos:
            produtos_e_marcas[key] = produtos_e_marcas.get(key, [])  # caso a chave não exista, criar a lista vazia
            produtos_e_marcas[key].append(value)
        return produtos_e_marcas

    @action(detail=False,
            methods=['POST'],
            url_path='filtro-por-parametros-agrupado-nome-marcas')
    def filtro_por_parametros_agrupado_nome_marcas(self, request):
        form = ProdutoPorParametrosForm(request.data)

        if not form.is_valid():
            return Response(form.errors)

        produtos_e_marcas = self.get_queryset_filtrado_agrupado(request, form)
        return Response(produtos_e_marcas)

    @action(detail=False,
            methods=['GET'],
            url_path='relatorio-por-parametros-agrupado-terceirizada')
    def relatorio_por_parametros_agrupado_terceirizada(self, request):
        form = ProdutoPorParametrosForm(request.GET)

        if not form.is_valid():
            return Response(form.errors)

        form_data = form.cleaned_data.copy()
        form_data['status'] = [
            HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
            HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU
        ]

        queryset = self.get_queryset_filtrado(form_data)

        dados_agrupados = agrupa_por_terceirizada(queryset)

        return relatorio_produtos_agrupado_terceirizada(request, dados_agrupados, form_data)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-relatorio-situacao-produto')
    def filtro_relatorio_situacao_produto(self, request):
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        return self.paginated_response(queryset.order_by('criado_em'))

    @action(detail=False,
            methods=['GET'],
            url_path='relatorio-situacao-produto')
    def relatorio_situacao_produto(self, request):
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        filtros = self.request.query_params.dict()
        return relatorio_produtos_situacao(
            request, queryset.order_by('criado_em'), filtros)

    # TODO: Remover esse endpoint legado refatorando o frontend
    @action(detail=False,
            methods=['POST'],
            url_path='filtro-homologados-por-parametros')
    def filtro_homologados_por_parametros(self, request):
        form = ProdutoPorParametrosForm(request.data)

        if not form.is_valid():
            return Response(form.errors)

        form_data = form.cleaned_data.copy()
        form_data['status'] = [
            HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
            HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
            HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE,
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProdutoWorkflow.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO,
            HomologacaoProdutoWorkflow.UE_RESPONDEU_QUESTIONAMENTO
        ]

        queryset = self.get_queryset_filtrado(form_data)
        return self.paginated_response(queryset.order_by('criado_em'))

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-reclamacoes-terceirizada',
            permission_classes=[UsuarioTerceirizada])
    def filtro_reclamacoes_terceirizada(self, request):
        filtro_homologacao = {'homologacao__reclamacoes__status':
                              ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA}
        filtro_reclamacao = {'status__in': [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA,
                                            ReclamacaoProdutoWorkflow.RESPONDIDO_TERCEIRIZADA
                                            ]}
        qtde_questionamentos = Count('homologacao__reclamacoes', filter=Q(
            homologacao__reclamacoes__status=ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA))

        queryset = self.filter_queryset(self.get_queryset()).filter(
            **filtro_homologacao).prefetch_related(
                Prefetch('homologacao__reclamacoes', queryset=ReclamacaoDeProduto.objects.filter(
                    **filtro_reclamacao))).annotate(
                        qtde_questionamentos=qtde_questionamentos).order_by('criado_em').distinct()

        return self.paginated_response(queryset)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-reclamacoes-escola')
    def filtro_reclamacoes_escola(self, request):
        user = self.request.user
        filtro_homologacao = {'homologacao__reclamacoes__status':
                              ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE,
                              'homologacao__reclamacoes__escola': user.vinculo_atual.instituicao}
        filtro_reclamacao = {'status__in': [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE,
                                            ReclamacaoProdutoWorkflow.RESPONDIDO_UE
                                            ],
                             'escola': user.vinculo_atual.instituicao}
        qtde_questionamentos = Count('homologacao__reclamacoes', filter=Q(
            homologacao__reclamacoes__status=ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE))

        queryset = self.filter_queryset(self.get_queryset()).filter(
            **filtro_homologacao).prefetch_related(
                Prefetch('homologacao__reclamacoes', queryset=ReclamacaoDeProduto.objects.filter(
                    **filtro_reclamacao))).annotate(
                        qtde_questionamentos=qtde_questionamentos).order_by('criado_em').distinct()

        return self.paginated_response(queryset)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-reclamacoes-nutrisupervisor')
    def filtro_reclamacoes_nutrisupervisor(self, request):
        user = self.request.user
        filtro_homologacao = {'homologacao__reclamacoes__status__in': [
                              ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
                              ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR],
                              'homologacao__reclamacoes__reclamante_registro_funcional': user.registro_funcional}
        filtro_reclamacao = {'status__in': [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
                                            ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR],
                             'reclamante_registro_funcional': user.registro_funcional}
        qtde_questionamentos = Count('homologacao__reclamacoes', filter=Q(
            homologacao__reclamacoes__status__in=[
                ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
                ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR]))

        queryset = self.filter_queryset(self.get_queryset()).filter(
            **filtro_homologacao).prefetch_related(
                Prefetch('homologacao__reclamacoes', queryset=ReclamacaoDeProduto.objects.filter(
                    **filtro_reclamacao))).annotate(
                        qtde_questionamentos=qtde_questionamentos).order_by('criado_em').distinct()

        return self.paginated_response(queryset)

    def filtra_produtos_em_analise_sensorial(self, request, queryset):
        data_analise_inicial = converte_para_datetime(
            request.query_params.get('data_analise_inicial', None))
        data_analise_final = converte_para_datetime(
            request.query_params.get('data_analise_final', None))
        para_excluir = []
        if data_analise_inicial or data_analise_final:
            filtros_data = get_filtros_data(
                data_analise_inicial, data_analise_final)
            for produto in queryset:
                ultima_homologacao = produto.homologacao
                ultima_resposta = ultima_homologacao.respostas_analise.last()
                log_analise = ultima_homologacao.logs.filter(
                    status_evento=LogSolicitacoesUsuario.CODAE_PEDIU_ANALISE_SENSORIAL,
                    **filtros_data
                ).filter(criado_em__lte=ultima_resposta.criado_em).order_by('criado_em').last()

                if log_analise is None:
                    para_excluir.append(produto.id)
        return queryset.exclude(id__in=para_excluir).order_by('nome',
                                                              'homologacao__rastro_terceirizada__nome_fantasia')

    def filtra_produtos_suspensos_por_data(self, request, queryset):
        data_suspensao_inicial = converte_para_datetime(
            request.query_params.get('data_suspensao_inicial', None))
        data_suspensao_final = converte_para_datetime(
            request.query_params.get('data_suspensao_final', None))
        para_excluir = []
        if data_suspensao_inicial or data_suspensao_final:
            filtros_data = get_filtros_data(
                data_suspensao_inicial, data_suspensao_final)
            for produto in queryset:
                ultima_homologacao = produto.homologacao
                ultimo_log = ultima_homologacao.ultimo_log
                log_suspensao = ultima_homologacao.logs.filter(
                    id=ultimo_log.id,
                    status_evento=LogSolicitacoesUsuario.CODAE_SUSPENDEU,
                    **filtros_data
                ).first()
                if log_suspensao is None:
                    para_excluir.append(produto.id)
        return queryset.exclude(id__in=para_excluir)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-relatorio-produto-suspenso')
    def filtro_relatorio_produto_suspenso(self, request):
        queryset = self.filter_queryset(self.get_queryset()).select_related(
            'marca', 'fabricante').order_by('nome')
        queryset = self.filtra_produtos_suspensos_por_data(request, queryset)
        return self.paginated_response(queryset)

    @action(detail=False, url_path='relatorio-produto-suspenso',
            methods=['GET'])
    def relatorio_produto_suspenso(self, request):
        queryset = self.filter_queryset(self.get_queryset()).select_related(
            'marca', 'fabricante').order_by('nome')
        queryset = self.filtra_produtos_suspensos_por_data(request, queryset)
        filtros = self.request.query_params.dict()
        return relatorio_produtos_suspensos(queryset, filtros)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-relatorio-em-analise-sensorial',
            permission_classes=[UsuarioTerceirizada | UsuarioCODAEGestaoProduto])
    def filtro_relatorio_em_analise_sensorial(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(homologacao__respostas_analise__isnull=False).prefetch_related(
                Prefetch('homologacao', queryset=HomologacaoProduto.objects.all().exclude(
                    respostas_analise__exact=None))).distinct()
        queryset = self.filtra_produtos_em_analise_sensorial(
            request, queryset).select_related('marca', 'fabricante')
        return self.paginated_response(queryset)

    @action(detail=False,
            methods=['GET'],
            url_path='relatorio-em-analise-sensorial',
            permission_classes=[UsuarioTerceirizada | UsuarioCODAEGestaoProduto])
    def relatorio_em_analise_sensorial(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(homologacao__respostas_analise__isnull=False).prefetch_related(
                Prefetch('homologacao', queryset=HomologacaoProduto.objects.all().exclude(
                    respostas_analise__exact=None))).distinct()
        queryset = self.filtra_produtos_em_analise_sensorial(
            request, queryset).select_related('marca', 'fabricante')
        filtros = self.request.query_params.dict()
        produtos = ProdutoRelatorioAnaliseSensorialSerializer(
            queryset, many=True).data
        return relatorio_produtos_em_analise_sensorial(produtos, filtros)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-reclamacoes')
    def filtro_reclamacoes(self, request):
        filtro_reclamacao, filtro_homologacao = filtros_produto_reclamacoes(
            request)
        queryset = self.filter_queryset(
            self.get_queryset()).filter(**filtro_homologacao).prefetch_related(
                Prefetch('homologacao__reclamacoes', queryset=ReclamacaoDeProduto.objects.filter(
                    **filtro_reclamacao))).order_by(
                        'nome').select_related('marca', 'fabricante').distinct()
        return self.paginated_response(queryset)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-avaliar-reclamacoes',
            permission_classes=[UsuarioCODAEGestaoProduto])
    def filtro_avaliar_reclamacoes(self, request):
        status_reclamacao = self.request.query_params.getlist(
            'status_reclamacao')
        queryset = self.filter_queryset(self.get_queryset()).prefetch_related('homologacao__reclamacoes').filter(
            homologacao__reclamacoes__status__in=status_reclamacao).order_by('nome').select_related(
                'marca', 'fabricante').distinct()
        return self.paginated_response(queryset)

    @action(detail=False,
            methods=['GET'],
            url_path='relatorio-reclamacao')
    def relatorio_reclamacao(self, request):
        filtro_reclamacao, filtro_homologacao = filtros_produto_reclamacoes(
            request)
        queryset = self.filter_queryset(
            self.get_queryset()).filter(**filtro_homologacao).prefetch_related(
                Prefetch('homologacao__reclamacoes', queryset=ReclamacaoDeProduto.objects.filter(
                    **filtro_reclamacao))).order_by(
                        'nome').distinct()
        filtros = self.request.query_params.dict()
        return relatorio_reclamacao(queryset, filtros)

    @action(detail=False, methods=['GET'], url_path='ja-existe')
    def ja_existe(self, request):
        form = ProdutoJaExisteForm(request.GET)

        if not form.is_valid():
            return Response(form.errors)

        queryset = self.get_queryset().filter(
            **form.cleaned_data).exclude(
                homologacao__status=HomologacaoProdutoWorkflow.RASCUNHO)

        return Response({
            'produto_existe': queryset.count() > 0
        })

    @action(detail=False, methods=['GET'], url_path='autocomplete-nomes')
    def autocomplete_nomes(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response({
            'count': queryset.count(),
            'results': [value[0] for value in queryset.values_list('nome')]
        })


class ProdutosEditaisViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = ProdutoEdital.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProdutoEditalCreateSerializer
        return ProdutoEditalSerializer

    @action(detail=True, methods=['patch'], url_path='ativar-inativar-produto')
    def ativar_inativar_produto(self, request, uuid=None):
        try:
            vinculo = ProdutoEdital.objects.get(uuid=uuid)
            if vinculo.ativo:
                vinculo.ativo = False
            else:
                vinculo.ativo = True
            vinculo.save()
            serializer = self.get_serializer(vinculo)
            return Response(dict(data=serializer.data),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(detail=f'Erro ao Ativar/inativar vínculo do produto com edital: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='filtros')
    def filtros(self, request):
        try:
            vinculos = self.get_queryset()
            produtos = vinculos.distinct('produto__nome').values('produto__nome', 'produto__uuid')
            editais = vinculos.distinct('edital__numero').values('edital__numero', 'edital__uuid')
            return Response(dict(produtos=produtos, editais=editais), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(detail=f'Erro ao consultar filtros: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='filtrar') # noqa c901
    def filtrar(self, request):
        queryset = self.get_queryset().order_by('produto__nome')
        nome = request.query_params.get('nome', None)
        edital = request.query_params.get('edital', None)
        tipo_dieta = request.query_params.get('tipo', None)
        if nome:
            queryset = queryset.filter(produto__nome__in=[nome])
        if edital:
            queryset = queryset.filter(edital__numero__in=[edital])
        if tipo_dieta:
            queryset = queryset.filter(tipo_produto=tipo_dieta)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['get'], url_path='lista-produtos-opcoes') # noqa c901
    def lista_produtos_opcoes(self, request):
        try:
            editais_uuid = request.query_params.get('editais', '')
            editais_uuid = editais_uuid.split(';')
            queryset = self.get_queryset().filter(edital__uuid__in=editais_uuid).distinct('produto__uuid')
            data = self.get_serializer(queryset, many=True).data
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(detail=f'Erro ao consultar produtos: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)


class NomeDeProdutoEditalViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = NomeDeProdutoEdital.objects.filter(ativo=True).all()
        data = NomeDeProdutoEditalSerializer(queryset, many=True).data
        return Response({'results': data})


class CadastroProdutoEditalViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = NomeDeProdutoEdital.objects.all()
    pagination_class = CadastroProdutosEditalPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CadastroProdutosEditalFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CadastroProdutosEditalCreateSerializer
        return CadastroProdutosEditalSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_de_nomes(self, _):
        return Response({'results': [item.nome for item in self.queryset.all()]})

    class Meta:
        model = NomeDeProdutoEdital


class ProtocoloDeDietaEspecialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProtocoloDeDietaEspecialSerializer
    queryset = ProtocoloDeDietaEspecial.objects.all()

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_protocolos(self, request):
        query_set = ProtocoloDeDietaEspecial.objects.filter(ativo=True)
        response = {'results': ProtocoloSimplesSerializer(
            query_set, many=True).data}
        return Response(response)


class FabricanteViewSet(viewsets.ModelViewSet, ListaNomesUnicos):
    lookup_field = 'uuid'
    serializer_class = FabricanteSerializer
    queryset = Fabricante.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_fabricantes(self, request):
        query_set = Fabricante.objects.all()
        filtrar_por = request.query_params.get('filtrar_por', None)
        if filtrar_por == 'reclamacoes/':
            query_set = query_set.filter(produto__homologacao__reclamacoes__isnull=False,
                                         produto__homologacao__status__in=['CODAE_PEDIU_ANALISE_RECLAMACAO',
                                                                           'TERCEIRIZADA_RESPONDEU_RECLAMACAO',
                                                                           'ESCOLA_OU_NUTRICIONISTA_RECLAMOU'])
        response = {'results': FabricanteSimplesSerializer(
            query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-nova-reclamacao')
    def lista_fabricantes_nova_reclamacao(self, request):
        query_set = Fabricante.objects.filter(
            produto__ativo=True,
            produto__homologacao__status__in=NOVA_RECLAMACAO_HOMOLOGACOES_STATUS
        ).distinct('nome')
        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-avaliar-reclamacao')
    def lista_fabricantes_avaliar_reclamacao(self, request):
        query_set = Fabricante.objects.filter(
            produto__homologacao__status__in=AVALIAR_RECLAMACAO_HOMOLOGACOES_STATUS,
            produto__homologacao__reclamacoes__status__in=AVALIAR_RECLAMACAO_RECLAMACOES_STATUS
        ).distinct()
        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao')
    def lista_fabricantes_responder_reclamacao(self, request):
        user = request.user
        query_set = Fabricante.objects.filter(
            produto__homologacao__status__in=RESPONDER_RECLAMACAO_HOMOLOGACOES_STATUS,
            produto__homologacao__reclamacoes__status__in=RESPONDER_RECLAMACAO_RECLAMACOES_STATUS,
            produto__homologacao__rastro_terceirizada=user.vinculo_atual.instituicao
        ).distinct()
        if user.tipo_usuario == 'terceirizada':
            query_set = query_set.filter(produto__homologacao__rastro_terceirizada=user.vinculo_atual.instituicao)
        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-escola')
    def lista_fabricantes_responder_reclamacao_escola(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE,
            HomologacaoProdutoWorkflow.UE_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE]

        query_set = Fabricante.objects.filter(
            produto__homologacao__status__in=status_homologacoes,
            produto__homologacao__reclamacoes__status__in=status_reclamacoes,
            produto__homologacao__reclamacoes__escola=user.vinculo_atual.instituicao
        ).distinct()

        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-nutrisupervisor')
    def lista_fabricantes_responder_reclamacao_nutrisupervisor(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProdutoWorkflow.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [
            ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
            ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR]

        query_set = Fabricante.objects.filter(
            produto__homologacao__status__in=status_homologacoes,
            produto__homologacao__reclamacoes__status__in=status_reclamacoes,
            produto__homologacao__reclamacoes__reclamante_registro_funcional=user.registro_funcional
        ).distinct()

        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)


class MarcaViewSet(viewsets.ModelViewSet, ListaNomesUnicos):
    lookup_field = 'uuid'
    serializer_class = MarcaSerializer
    queryset = Marca.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_marcas(self, request):
        query_set = Marca.objects.all()
        filtrar_por = request.query_params.get('filtrar_por', None)
        if filtrar_por == 'reclamacoes/':
            query_set = query_set.filter(produto__homologacao__reclamacoes__isnull=False,
                                         produto__homologacao__status__in=['CODAE_PEDIU_ANALISE_RECLAMACAO',
                                                                           'TERCEIRIZADA_RESPONDEU_RECLAMACAO',
                                                                           'ESCOLA_OU_NUTRICIONISTA_RECLAMOU'])
        response = {'results': MarcaSimplesSerializer(
            query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-nova-reclamacao')
    def lista_marcas_nova_reclamacao(self, request):
        query_set = Marca.objects.filter(
            produto__ativo=True,
            produto__homologacao__status__in=NOVA_RECLAMACAO_HOMOLOGACOES_STATUS
        ).distinct('nome')
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-avaliar-reclamacao')
    def lista_marcas_avaliar_reclamacao(self, request):
        query_set = Marca.objects.filter(
            produto__homologacao__status__in=AVALIAR_RECLAMACAO_HOMOLOGACOES_STATUS,
            produto__homologacao__reclamacoes__status__in=AVALIAR_RECLAMACAO_RECLAMACOES_STATUS
        ).distinct()
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao')
    def lista_marcas_responder_reclamacao(self, request):
        user = request.user
        query_set = Marca.objects.filter(
            produto__homologacao__status__in=RESPONDER_RECLAMACAO_HOMOLOGACOES_STATUS,
            produto__homologacao__reclamacoes__status__in=RESPONDER_RECLAMACAO_RECLAMACOES_STATUS,
            produto__homologacao__rastro_terceirizada=user.vinculo_atual.instituicao
        ).distinct()
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-escola')
    def lista_marcas_responder_reclamacao_escola(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE,
            HomologacaoProdutoWorkflow.UE_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE]

        query_set = Marca.objects.filter(
            produto__homologacao__status__in=status_homologacoes,
            produto__homologacao__reclamacoes__status__in=status_reclamacoes,
            produto__homologacao__reclamacoes__escola=user.vinculo_atual.instituicao
        ).distinct()
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-responder-reclamacao-nutrisupervisor')
    def lista_marcas_responder_reclamacao_nutrisupervisor(self, request):
        user = request.user
        status_homologacoes = [
            HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR,
            HomologacaoProdutoWorkflow.NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO]

        status_reclamacoes = [
            ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
            ReclamacaoProdutoWorkflow.RESPONDIDO_NUTRISUPERVISOR]

        query_set = Marca.objects.filter(
            produto__homologacao__status__in=status_homologacoes,
            produto__homologacao__reclamacoes__status__in=status_reclamacoes,
            produto__homologacao__reclamacoes__reclamante_registro_funcional=user.registro_funcional
        ).distinct()
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)


class InformacaoNutricionalViewSet(InformacaoNutricionalBaseViewSet):
    lookup_field = 'uuid'
    serializer_class = InformacaoNutricionalSerializer
    queryset = InformacaoNutricional.objects.all()

    @action(detail=False, methods=['GET'], url_path=f'agrupadas')
    def informacoes_nutricionais_agrupadas(self, request):
        query_set = InformacaoNutricional.objects.all().order_by('id')
        response = {'results': self._agrupa_informacoes_por_tipo(query_set)}
        return Response(response)


class RespostaAnaliseSensorialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = RespostaAnaliseSensorialSearilzerCreate
    queryset = RespostaAnaliseSensorial.objects.all()

    @action(detail=False, # noqa C901
            permission_classes=[UsuarioTerceirizada],
            methods=['post'],
            url_path=constants.TERCEIRIZADA_RESPONDE_ANALISE_SENSORIAL)
    def terceirizada_responde(self, request):
        data = request.data.copy()
        uuid_homologacao = data.pop('homologacao_de_produto', None)
        data['homologacao_produto'] = uuid_homologacao
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        homologacao = HomologacaoProduto.objects.get(uuid=uuid_homologacao)
        data['homologacao_produto'] = homologacao
        try:
            serializer.create(data)
            justificativa = request.data.get('justificativa', '')
            if not justificativa:
                justificativa = data.get('observacao', '')

            reclamacao = homologacao.reclamacoes.filter(
                status=ReclamacaoProdutoWorkflow.AGUARDANDO_ANALISE_SENSORIAL).first()
            if reclamacao:
                # Respondendo análise sensorial vindo de uma Homologação de produto em processo de reclamação.
                reclamacao.terceirizada_responde_analise_sensorial(user=request.user, justificativa=justificativa)
                # Assim a homologação volta a aparecer no card de aguardando análise reclamações.
                homologacao.terceirizada_responde_analise_sensorial_da_reclamacao(
                    user=request.user, justificativa=justificativa
                )
            else:
                # Respondendo análise sensorial vindo de uma Homologação de produto homologada.
                logs_homologados = homologacao.logs.filter(status_evento=LogSolicitacoesUsuario.CODAE_HOMOLOGADO).all()

                # Essa validação não está funcionando
                # caso de erro:
                # Tercerizada Solicitou > CODAE Homologou > CODAE Suspendeu
                # Terceirzada Corrigiu > CODAE Solicita análise sensorial
                # Produto vai direto para homologado
                # o último log de CODAE_HOMOLOGADO deve ser novo que o último log de CODAE_PENDENTE_HOMOLOGACAO
                if logs_homologados:
                    homologacao.terceirizada_responde_analise_sensorial_homologado(
                        user=request.user, justificativa=justificativa
                    )
                else:
                    # Respondendo análise sensorial vindo de uma Homologação de produto pendente.
                    homologacao.terceirizada_responde_analise_sensorial(
                        user=request.user, justificativa=justificativa
                    )
            serializer.save()

            analise_sensorial = homologacao.ultima_analise
            if analise_sensorial:
                analise_sensorial.status = AnaliseSensorial.STATUS_RESPONDIDA
                analise_sensorial.save()

            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)


class ReclamacaoProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    lookup_field = 'uuid'
    serializer_class = ReclamacaoDeProdutoSerializer
    queryset = ReclamacaoDeProduto.objects.all()

    def muda_status_com_justificativa_e_anexo(self, request, metodo_transicao):
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        try:
            metodo_transicao(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )
            serializer = self.get_serializer(self.get_object())
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_ACEITA)
    def codae_aceita(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        reclamacao_produto.homologacao_produto.codae_autorizou_reclamacao(
            user=request.user,
            anexos=anexos,
            justificativa=justificativa
        )
        analises_sensoriais = reclamacao_produto.homologacao_produto.analises_sensoriais.filter(
            status=AnaliseSensorial.STATUS_AGUARDANDO_RESPOSTA).all()
        if analises_sensoriais:
            for analise_sensorial in analises_sensoriais:
                analise_sensorial.status = AnaliseSensorial.STATUS_RESPONDIDA
                analise_sensorial.save()

        return self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_aceita)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_RECUSA)
    def codae_recusa(self, request, uuid=None):
        from sme_terceirizadas.produto.models import AnaliseSensorial
        reclamacao_produto = self.get_object()
        resposta = self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_recusa)
        reclamacoes_ativas = reclamacao_produto.homologacao_produto.reclamacoes.filter(
            status__in=[
                ReclamacaoProdutoWorkflow.AGUARDANDO_AVALIACAO,
                ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA,
                ReclamacaoProdutoWorkflow.RESPONDIDO_TERCEIRIZADA,
                ReclamacaoProdutoWorkflow.AGUARDANDO_ANALISE_SENSORIAL,
                ReclamacaoProdutoWorkflow.ANALISE_SENSORIAL_RESPONDIDA,
            ]
        )
        if reclamacoes_ativas.count() == 0:
            reclamacao_produto.homologacao_produto.codae_recusou_reclamacao(
                user=request.user,
                justificativa=request.data.get('justificativa') or 'Recusa automática por não haver mais reclamações'
            )

        analises_sensoriais = reclamacao_produto.homologacao_produto.analises_sensoriais.filter(
            status=AnaliseSensorial.STATUS_AGUARDANDO_RESPOSTA).all()
        if analises_sensoriais:
            for analise_sensorial in analises_sensoriais:
                analise_sensorial.status = AnaliseSensorial.STATUS_RESPONDIDA
                analise_sensorial.save()
        return resposta

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_TERCEIRIZADA)
    def codae_questiona_terceirizada(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        homologacao_produto = reclamacao_produto.homologacao_produto
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        status_homologacao = homologacao_produto.status
        if status_homologacao != HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO:
            homologacao_produto.codae_pediu_analise_reclamacao(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )
            homologacao_produto.rastro_terceirizada = reclamacao_produto.escola.lote.terceirizada
            homologacao_produto.save()
        return self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_questiona_terceirizada)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_UE)
    def codae_questiona_ue(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        homologacao_produto = reclamacao_produto.homologacao_produto
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        status_homologacao = homologacao_produto.status
        if status_homologacao != HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE:
            homologacao_produto.codae_questiona_ue(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )
            homologacao_produto.save()

        return self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_questiona_ue)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_NUTRISUPERVISOR)
    def codae_questiona_nutrisupervisor(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        homologacao_produto = reclamacao_produto.homologacao_produto
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        status_homologacao = homologacao_produto.status
        if status_homologacao != HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR:
            homologacao_produto.codae_questiona_nutrisupervisor(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )
            homologacao_produto.save()

        return self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_questiona_nutrisupervisor)

    @action(detail=True,
            permission_classes=[UsuarioCODAEGestaoProduto],
            methods=['patch'],
            url_path=constants.CODAE_RESPONDE)
    def codae_responde(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        return self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.codae_responde)

    @action(detail=True,
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_RESPONDE)
    def terceirizada_responde(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        resposta = self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.terceirizada_responde)
        questionamentos_ativas = reclamacao_produto.homologacao_produto.reclamacoes.filter(
            status__in=[
                ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA,
            ]
        )
        if questionamentos_ativas.count() == 0:
            reclamacao_produto.homologacao_produto.terceirizada_responde_reclamacao(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa,
                request=request)
        return resposta

    @action(detail=True,
            methods=['patch'],
            url_path=constants.ESCOLA_RESPONDE)
    def escola_responde(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        resposta = self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.ue_responde)
        questionamentos_ativos = reclamacao_produto.homologacao_produto.reclamacoes.filter(
            status__in=[
                ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE,
            ]
        )
        if questionamentos_ativos.count() == 0:
            reclamacao_produto.homologacao_produto.ue_respondeu_questionamento(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa,
                request=request)
        return resposta

    @action(detail=True,
            methods=['patch'],
            url_path=constants.NUTRISUPERVISOR_RESPONDE)
    def nutrisupervisor_responde(self, request, uuid=None):
        reclamacao_produto = self.get_object()
        anexos = request.data.get('anexos', [])
        justificativa = request.data.get('justificativa', '')
        resposta = self.muda_status_com_justificativa_e_anexo(
            request,
            reclamacao_produto.nutrisupervisor_responde)
        questionamentos_ativos = reclamacao_produto.homologacao_produto.reclamacoes.filter(
            status__in=[
                ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR,
            ]
        )
        if questionamentos_ativos.count() == 0:
            reclamacao_produto.homologacao_produto.nutrisupervisor_respondeu_questionamento(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa,
                request=request)
        return resposta

    @action(detail=True, # noqa C901
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_PEDE_ANALISE_SENSORIAL)
    def codae_pede_analise_sensorial(self, request, uuid=None):
        from sme_terceirizadas.produto.models import AnaliseSensorial
        from sme_terceirizadas.terceirizada.models import Terceirizada

        reclamacao_produto = self.get_object()
        homologacao_produto = reclamacao_produto.homologacao_produto
        uri = reverse(
            'Produtos-relatorio',
            args=[homologacao_produto.produto.uuid]
        )
        try:
            anexos = request.data.get('anexos', [])
            justificativa = request.data.get('justificativa', '')
            terceirizada_uuid = request.data.get('uuidTerceirizada', '')
            if not terceirizada_uuid:
                return Response({'detail': 'O uuid da terceirizada é obrigatório'})

            terceirizada = Terceirizada.objects.filter(uuid=terceirizada_uuid).first()
            if not terceirizada:
                return Response({'detail': f'Terceirizada para uuid {terceirizada_uuid} não encontrado.'})

            AnaliseSensorial.objects.create(
                homologacao_produto=homologacao_produto,
                terceirizada=terceirizada)

            homologacao_produto.gera_protocolo_analise_sensorial()
            homologacao_produto.codae_pede_analise_sensorial(
                user=request.user, justificativa=justificativa,
                link_pdf=url_configs('API', {'uri': uri})
            )

            reclamacao_produto.codae_pede_analise_sensorial(
                user=request.user,
                anexos=anexos,
                justificativa=justificativa
            )

            serializer = self.get_serializer(self.get_object())
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)


class SolicitacaoCadastroProdutoDietaFilter(filters.FilterSet):
    nome_produto = filters.CharFilter(
        field_name='nome_produto', lookup_expr='icontains')
    data_inicial = filters.DateFilter(
        field_name='criado_em', lookup_expr='date__gte')
    data_final = filters.DateFilter(
        field_name='criado_em', lookup_expr='date__lte')
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = SolicitacaoCadastroProdutoDieta
        fields = ['nome_produto', 'data_inicial', 'data_final', 'status']


class SolicitacaoCadastroProdutoDietaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoCadastroProdutoDieta.objects.all().order_by('-criado_em')
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SolicitacaoCadastroProdutoDietaFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoCadastroProdutoDietaSerializerCreate
        return SolicitacaoCadastroProdutoDietaSerializer

    @action(detail=False, methods=['GET'], url_path='nomes-produtos')
    def nomes_produtos(self, request):
        return Response([s.nome_produto for s in SolicitacaoCadastroProdutoDieta.objects.only('nome_produto')])

    @transaction.atomic
    @action(detail=True, methods=['patch'], url_path='confirma-previsao')
    def confirma_previsao(self, request, uuid=None):
        solicitacao = self.get_object()
        serializer = self.get_serializer()
        try:
            serializer.update(solicitacao, request.data)
            solicitacao.terceirizada_atende_solicitacao(user=request.user)
            return Response({'detail': 'Confirmação de previsão de cadastro realizada com sucesso'})
        except InvalidTransitionError as e:
            return Response({'detail': f'Erro na transição de estado {e}'}, status=HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos {e}'}, status=HTTP_400_BAD_REQUEST)


class ItensCadastroViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = ItemCadastro.objects.all().order_by('-criado_em')
    pagination_class = ItemCadastroPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ItemCadastroFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ItensCadastroCreateSerializer
        return ItensCadastroSerializer

    @action(detail=False, methods=['GET'], url_path='tipos')
    def tipos(self, _):
        return Response([{'tipo': choice[0], 'tipo_display': choice[1]} for choice in ItemCadastro.CHOICES])

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_de_nomes(self, _):
        return Response({'results': [item.content_object.nome for item in self.queryset.all()]})

    def destroy(self, request, *args, **kwargs):
        instance: ItemCadastro = self.get_object()

        if instance.deleta_modelo():
            return Response(status=status.HTTP_204_NO_CONTENT)

        msg = 'Não será possível realizar a exclusão. Este item contém relacionamentos com Cadastro de Produtos.'
        return Response(data={'detail': msg}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        model = ItemCadastro


class UnidadesDeMedidaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = UnidadeMedidaSerialzer
    queryset = UnidadeMedida.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class EmbalagemProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EmbalagemProdutoSerialzer
    queryset = EmbalagemProduto.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
