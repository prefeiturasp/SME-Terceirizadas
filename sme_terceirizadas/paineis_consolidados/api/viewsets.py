import datetime
import unicodedata

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from ...dados_comuns.constants import FILTRO_PADRAO_PEDIDOS, SEM_FILTRO
from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ...dados_comuns.permissions import (
    PermissaoParaRecuperarDietaEspecial,
    UsuarioCODAEGestaoAlimentacao,
    UsuarioDiretoriaRegional,
    UsuarioEscolaTercTotal,
    UsuarioNutricionista,
    UsuarioTerceirizada
)
from ...dados_comuns.utils import get_ultimo_dia_mes
from ...dieta_especial.api.serializers import SolicitacaoDietaEspecialLogSerializer, SolicitacaoDietaEspecialSerializer
from ...dieta_especial.models import SolicitacaoDietaEspecial
from ...paineis_consolidados.api.constants import PESQUISA, TIPO_VISAO, TIPO_VISAO_LOTE, TIPO_VISAO_SOLICITACOES
from ...paineis_consolidados.api.serializers import SolicitacoesSerializer
from ...relatorios.relatorios import relatorio_filtro_periodo, relatorio_resumo_anual_e_mensal
from ..api.constants import PENDENTES_VALIDACAO_DRE, RELATORIO_PERIODO
from ..models import (
    MoldeConsolidado,
    SolicitacoesCODAE,
    SolicitacoesDRE,
    SolicitacoesEscola,
    SolicitacoesNutrimanifestacao,
    SolicitacoesNutrisupervisao,
    SolicitacoesTerceirizada
)
from ..tasks import gera_pdf_relatorio_solicitacoes_alimentacao_async, gera_xls_relatorio_solicitacoes_alimentacao_async
from ..utils import (
    formata_resultado_inclusoes_etec_autorizadas,
    tratar_data_evento_final_no_mes,
    tratar_dias_duplicados
)
from ..validators import FiltroValidator
from .constants import (
    AGUARDANDO_CODAE,
    AGUARDANDO_INICIO_VIGENCIA_DIETA_ESPECIAL,
    ALTERACOES_ALIMENTACAO_AUTORIZADAS,
    AUTORIZADAS_TEMPORARIAMENTE_DIETA_ESPECIAL,
    AUTORIZADOS,
    AUTORIZADOS_DIETA_ESPECIAL,
    CANCELADOS,
    CANCELADOS_DIETA_ESPECIAL,
    FILTRO_DRE_UUID,
    FILTRO_ESCOLA_UUID,
    FILTRO_TERCEIRIZADA_UUID,
    INATIVAS_DIETA_ESPECIAL,
    INATIVAS_TEMPORARIAMENTE_DIETA_ESPECIAL,
    INCLUSOES_AUTORIZADAS,
    INCLUSOES_ETEC_AUTORIZADAS,
    KIT_LANCHES_AUTORIZADAS,
    NEGADOS,
    NEGADOS_DIETA_ESPECIAL,
    PENDENTES_AUTORIZACAO,
    PENDENTES_AUTORIZACAO_DIETA_ESPECIAL,
    PENDENTES_CIENCIA,
    QUESTIONAMENTOS,
    RELATORIO_RESUMO_MES_ANO,
    RESUMO_ANO,
    RESUMO_MES,
    SUSPENSOES_AUTORIZADAS
)
from .filters import SolicitacoesCODAEFilter


class SolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    @classmethod
    def remove_duplicados_do_query_set(self, query_set):
        """_remove_duplicados_do_query_set é criado por não ser possível juntar order_by e distinct na mesma query."""
        # TODO: se alguém descobrir como ordenar a query e tirar os uuids
        # repetidos, por favor melhore
        aux = []
        sem_uuid_repetido = []
        for resultado in query_set:
            if resultado.uuid not in aux:
                aux.append(resultado.uuid)
                sem_uuid_repetido.append(resultado)
        return sem_uuid_repetido

    def _retorno_base(self, query_set, sem_paginacao=None):
        sem_uuid_repetido = self.remove_duplicados_do_query_set(query_set)
        if sem_paginacao:
            serializer = self.get_serializer(sem_uuid_repetido, many=True)
            return Response({'results': serializer.data})
        page = self.paginate_queryset(sem_uuid_repetido)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def _agrupar_solicitacoes(self, tipo_visao: str, query_set: QuerySet):
        if tipo_visao == TIPO_VISAO_SOLICITACOES:
            descricao_prioridade = [(solicitacao.desc_doc, solicitacao.prioridade) for solicitacao in query_set
                                    if solicitacao.prioridade != 'VENCIDO']
        elif tipo_visao == TIPO_VISAO_LOTE:
            descricao_prioridade = [(solicitacao.lote_nome, solicitacao.prioridade) for solicitacao in query_set
                                    if solicitacao.prioridade != 'VENCIDO']
        else:
            descricao_prioridade = [(solicitacao.dre_nome, solicitacao.prioridade) for solicitacao in query_set
                                    if solicitacao.prioridade != 'VENCIDO']
        return descricao_prioridade

    def _agrupa_por_tipo_visao(self, tipo_visao: str, query_set: QuerySet) -> dict:
        sumario = {}  # type: dict
        query_set = self.remove_duplicados_do_query_set(query_set)
        descricao_prioridade = self._agrupar_solicitacoes(
            tipo_visao, query_set)
        for nome_objeto, prioridade in descricao_prioridade:
            if nome_objeto == 'Inclusão de Alimentação Contínua':
                nome_objeto = 'Inclusão de Alimentação'
            if nome_objeto not in sumario:
                sumario[nome_objeto] = {'TOTAL': 0,
                                        'REGULAR': 0,
                                        'PRIORITARIO': 0,
                                        'LIMITE': 0}
            sumario[nome_objeto][prioridade] += 1
            sumario[nome_objeto]['TOTAL'] += 1
        return sumario

    def _agrupa_por_mes_por_solicitacao(self, query_set: list) -> dict:
        # TODO: melhorar performance
        sumario = {
            'total': 0,
            'Inclusão de Alimentação': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Alteração do tipo de Alimentação': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Inversão de dia de Cardápio': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Suspensão de Alimentação': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Kit Lanche Passeio': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Kit Lanche Passeio Unificado': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
            'Dieta Especial': {
                'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'total': 0
            },
        }  # type: dict
        for solicitacao in query_set:
            if solicitacao['desc_doc'] == 'Inclusão de Alimentação Contínua':
                solicitacao['desc_doc'] = 'Inclusão de Alimentação'
            sumario[solicitacao['desc_doc']]['quantidades'][
                solicitacao['criado_em__month'] - 1] += 1
            sumario[solicitacao['desc_doc']]['total'] += 1
            sumario['total'] += 1
        return sumario

    def _retorna_data_ou_falso(self, date_text):
        try:
            return datetime.datetime.strptime(date_text, '%d-%m-%Y')
        except ValueError:
            return False

    @action(detail=False,
            methods=['GET'],
            url_path='solicitacoes-detalhadas')
    def solicitacoes_detalhadas(self, request):
        solicitacoes = request.query_params.getlist('solicitacoes[]', None)
        solicitacoes = MoldeConsolidado.solicitacoes_detalhadas(solicitacoes, request)
        return Response(dict(data=solicitacoes, status=HTTP_200_OK))


class NutrisupervisaoSolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    queryset = SolicitacoesNutrisupervisao.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}/{FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioNutricionista,))
    def pendentes_autorizacao(self, request, filtro_aplicado=SEM_FILTRO):
        query_set = SolicitacoesNutrisupervisao.get_pendentes_autorizacao(
            filtro=filtro_aplicado)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=AUTORIZADOS,
            permission_classes=(UsuarioNutricionista,))
    def autorizados(self, request):
        query_set = SolicitacoesNutrisupervisao.get_autorizados()
        query_set = SolicitacoesNutrisupervisao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=NEGADOS,
            permission_classes=(UsuarioNutricionista,))
    def negados(self, request):
        query_set = SolicitacoesNutrisupervisao.get_negados()
        query_set = SolicitacoesNutrisupervisao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=CANCELADOS,
            permission_classes=(UsuarioNutricionista,))
    def cancelados(self, request):
        query_set = SolicitacoesNutrisupervisao.get_cancelados()
        query_set = SolicitacoesNutrisupervisao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}/{FILTRO_PADRAO_PEDIDOS}/{TIPO_VISAO}')
    def pendentes_autorizacao_secao_pendencias(self, request,
                                               filtro_aplicado=SEM_FILTRO,
                                               tipo_visao=TIPO_VISAO_SOLICITACOES):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao(dre_uuid=diretoria_regional.uuid,
                                                                filtro=filtro_aplicado)
        response = {'results': self._agrupa_por_tipo_visao(
            tipo_visao=tipo_visao, query_set=query_set)}

        return Response(response)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}')
    def pendentes_autorizacao_sem_filtro(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao(dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesNutrisupervisao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=QUESTIONAMENTOS,
            permission_classes=(UsuarioNutricionista,))
    def questionamentos(self, request):
        query_set = SolicitacoesCODAE.get_questionamentos()
        query_set = SolicitacoesNutrisupervisao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)


class NutrimanifestacaoSolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    queryset = SolicitacoesNutrimanifestacao.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False,
            methods=['GET'],
            url_path=AUTORIZADOS,
            permission_classes=(UsuarioNutricionista,))
    def autorizados(self, request):
        query_set = SolicitacoesNutrimanifestacao.get_autorizados()
        query_set = SolicitacoesNutrimanifestacao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=NEGADOS,
            permission_classes=(UsuarioNutricionista,))
    def negados(self, request):
        query_set = SolicitacoesNutrimanifestacao.get_negados()
        query_set = SolicitacoesNutrimanifestacao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=CANCELADOS,
            permission_classes=(UsuarioNutricionista,))
    def cancelados(self, request):
        query_set = SolicitacoesNutrimanifestacao.get_cancelados()
        query_set = SolicitacoesNutrimanifestacao.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)


class CODAESolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    queryset = SolicitacoesCODAE.objects.all()
    serializer_class = SolicitacoesSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SolicitacoesCODAEFilter

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}/{FILTRO_PADRAO_PEDIDOS}/{TIPO_VISAO}')
    def pendentes_autorizacao_secao_pendencias(self, request,
                                               filtro_aplicado=SEM_FILTRO,
                                               tipo_visao=TIPO_VISAO_SOLICITACOES):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao(dre_uuid=diretoria_regional.uuid,
                                                                filtro=filtro_aplicado)
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        response = {'results': self._agrupa_por_tipo_visao(
            tipo_visao=tipo_visao, query_set=query_set)}

        return Response(response)

    @action(detail=False,
            methods=['GET'],
            url_path=PENDENTES_AUTORIZACAO_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def pendentes_autorizacao_dieta_especial(self, request):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_pendentes_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=AUTORIZADOS_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def autorizados_dieta_especial(self, request):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_autorizados_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=NEGADOS_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def negados_dieta_especial(self, request):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_negados_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=CANCELADOS_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def cancelados_dieta_especial(self, request):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_cancelados_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=AUTORIZADAS_TEMPORARIAMENTE_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def autorizadas_temporariamente_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_autorizadas_temporariamente_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=INATIVAS_TEMPORARIAMENTE_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def inativas_temporariamente_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_inativas_temporariamente_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=INATIVAS_DIETA_ESPECIAL,
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def inativas_dieta_especial(self, request):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesCODAE.get_inativas_dieta_especial()
        query_set = SolicitacoesCODAE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}/{FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def pendentes_autorizacao(self, request, filtro_aplicado=SEM_FILTRO):
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao(
            filtro=filtro_aplicado)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO}',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def pendentes_autorizacao_sem_filtro(self, request):
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao()
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=AUTORIZADOS,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def autorizados(self, request):
        query_set = SolicitacoesCODAE.get_autorizados()
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=NEGADOS,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def negados(self, request):
        query_set = SolicitacoesCODAE.get_negados()
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=CANCELADOS,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def cancelados(self, request):
        query_set = SolicitacoesCODAE.get_cancelados()
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=QUESTIONAMENTOS,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def questionamentos(self, request):
        query_set = SolicitacoesCODAE.get_questionamentos()
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{PESQUISA}/{FILTRO_DRE_UUID}/{FILTRO_ESCOLA_UUID}',
        permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def filtro_periodo_tipo_solicitacao(self, request, escola_uuid=None, dre_uuid=None):
        """Filtro de todas as solicitações da  codae.

        ---
        tipo_solicitacao -- ALT_CARDAPIO|INV_CARDAPIO|INC_ALIMENTA|INC_ALIMENTA_CONTINUA|
        KIT_LANCHE_AVULSA|SUSP_ALIMENTACAO|KIT_LANCHE_UNIFICADA|TODOS
        status_solicitacao -- AUTORIZADOS|NEGADOS|CANCELADOS|RECEBIDAS|TODOS
        data_inicial -- dd-mm-yyyy
        data_final -- dd-mm-yyyy
        """
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesCODAE.filtros_codae(
                escola_uuid=escola_uuid,
                dre_uuid=dre_uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            return self._retorno_base(query_set)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RESUMO_MES}',
        permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def resumo_mes(self, request):
        totais_dict = SolicitacoesCODAE.resumo_totais_mes()
        return Response(totais_dict)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_RESUMO_MES_ANO}',
        permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def relatorio_resumo_anual_e_mensal(self, request):
        query_set = SolicitacoesCODAE.get_solicitacoes_ano_corrente()
        resumo_do_ano = self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)
        resumo_do_mes = SolicitacoesCODAE.resumo_totais_mes()
        return relatorio_resumo_anual_e_mensal(request, resumo_do_mes, resumo_do_ano)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_PERIODO}/{FILTRO_DRE_UUID}/{FILTRO_ESCOLA_UUID}',
        permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def relatorio_filtro_periodo(self, request, escola_uuid=None, dre_uuid=None):
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesCODAE.filtros_codae(
                escola_uuid=escola_uuid,
                dre_uuid=dre_uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            query_set = self.remove_duplicados_do_query_set(query_set)

            return relatorio_filtro_periodo(request, query_set)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{RESUMO_ANO}',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def evolucao_solicitacoes(self, request):
        # TODO: verificar se a pessoa é do lugar certo da codae
        query_set = SolicitacoesCODAE.get_solicitacoes_ano_corrente()
        response = {'results': self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)}
        return Response(response)

    def filtrar_solicitacoes_para_relatorio(self, request):
        status = request.query_params.get('status', None)
        queryset = SolicitacoesCODAE.map_queryset_por_status(status)

        # filtra por datas
        periodo_datas = {
            'data_evento': request.query_params.get('de', None),
            'data_evento_fim': request.query_params.get('ate', None)
        }
        queryset = SolicitacoesCODAE.busca_periodo_de_datas(queryset, periodo_datas)

        tipo_doc = request.query_params.getlist('tipos_solicitacao[]', None)
        tipo_doc = SolicitacoesCODAE.map_queryset_por_tipo_doc(tipo_doc)
        # outros filtros
        map_filtros = {
            'lote_uuid__in': request.query_params.getlist('lotes[]', None),
            'escola_uuid__in': request.query_params.getlist('unidades_educacionais[]', None),
            'terceirizada_uuid': request.query_params.get('terceirizada', None),
            'tipo_doc__in': tipo_doc,
            'escola_tipo_unidade_uuid__in': request.query_params.getlist('tipos_unidade[]', None),
        }
        filtros = {key: value for key, value in map_filtros.items() if value not in [None, []]}
        queryset = queryset.filter(**filtros)
        return queryset

    @action(detail=False,
            methods=['GET'],
            url_path='filtrar-solicitacoes-ga',
            permission_classes=([UsuarioCODAEGestaoAlimentacao | UsuarioNutricionista]))
    def filtrar_solicitacoes_ga(self, request):
        # queryset por status
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        return self._retorno_base(queryset, False)

    @action(detail=False, methods=['GET'], url_path='exportar-xlsx')
    def exportar_xlsx(self, request):
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        lotes = request.query_params.getlist('lotes[]')
        tipos_solicitacao = request.query_params.getlist('tipos_solicitacao[]')
        tipos_unidade = request.query_params.getlist('tipos_unidade[]')
        unidades_educacionais = request.query_params.getlist('unidades_educacionais[]')

        user = request.user.get_username()
        gera_xls_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.xlsx',
            data=self.request.query_params,
            uuids=uuids,
            lotes=lotes,
            tipos_solicitacao=tipos_solicitacao,
            tipos_unidade=tipos_unidade,
            unidades_educacionais=unidades_educacionais
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        user = request.user.get_username()
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        gera_pdf_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.pdf',
            data=self.request.query_params,
            uuids=uuids,
            status=request.query_params.get('status', None)
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)


class EscolaSolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesEscola.objects.all()
    permission_classes = (
        IsAuthenticated, PermissaoParaRecuperarDietaEspecial,)
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO}')
    def pendentes_autorizacao(self, request):
        escola_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesEscola.get_pendentes_autorizacao(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def pendentes_autorizacao_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_pendentes_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def autorizados_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_autorizados_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{AUTORIZADAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def autorizadas_temporariamente_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_autorizadas_temporariamente_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{AGUARDANDO_INICIO_VIGENCIA_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def aguardando_inicio_vigencia_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_aguardando_vigencia_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{INATIVAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def inativas_temporariamente_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_inativas_temporariamente_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{INATIVAS_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}',
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def inativas_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_inativas_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def negados_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_negados_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS_DIETA_ESPECIAL}/{FILTRO_ESCOLA_UUID}')
    def cancelados_dieta_especial(self, request, escola_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesEscola.get_cancelados_dieta_especial(
            escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}')
    def autorizados(self, request):
        escola_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{INCLUSOES_AUTORIZADAS}')
    def inclusoes_autorizadas(self, request):  # noqa C901
        escola_uuid = request.query_params.get('escola_uuid')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')
        date = datetime.date(int(ano), int(mes), 1)
        periodos_escolares = request.query_params.getlist('periodos_escolares[]')

        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        query_set = query_set.filter(
            Q(data_evento__month=mes, data_evento__year=ano) |
            Q(data_evento__lt=date, data_evento_2__gte=date)
        )
        query_set = query_set.filter(
            data_evento__lt=datetime.date.today()
        )
        query_set = self.remove_duplicados_do_query_set(query_set)

        return_dict = []

        def append(dia, periodo, inclusao):
            if (get_ultimo_dia_mes(datetime.date(int(ano), int(mes), 1)) < datetime.date.today() or
                    dia < datetime.date.today().day):
                alimentacoes = ', '.join([
                    unicodedata.normalize('NFD', alimentacao.nome.replace(' ', '_')).encode(
                        'ascii', 'ignore').decode('utf-8') for alimentacao in periodo.tipos_alimentacao.all()]).lower()
                return_dict.append({
                    'dia': f'{dia:02d}',
                    'periodo': f'{periodo.periodo_escolar.nome}',
                    'alimentacoes': alimentacoes,
                    'numero_alunos': periodo.numero_alunos,
                    'dias_semana': periodo.dias_semana,
                    'inclusao_id_externo': inclusao.id_externo
                })

        for inclusao in query_set:
            inc = inclusao.get_raw_model.objects.get(uuid=inclusao.uuid)
            for periodo in inc.quantidades_periodo.all():
                if periodo.periodo_escolar.nome in periodos_escolares:
                    if inclusao.tipo_doc == 'INC_ALIMENTA_CONTINUA':
                        i = inclusao.data_evento.day
                        big_range = False
                        if inclusao.data_evento.month != int(mes) and inclusao.data_evento_2.month != int(mes):
                            big_range = True
                            i = datetime.date(int(ano), int(mes), 1)
                            data_evento_final_no_mes = (i + relativedelta(day=31)).day
                            i = datetime.date(int(ano), int(mes), 1).day
                        else:
                            data_evento_final_no_mes = inclusao.data_evento_2.day
                        if inclusao.data_evento_2.month != inclusao.data_evento.month and not big_range:
                            data_evento_final_no_mes = (inclusao.data_evento + relativedelta(day=31)).day
                        while i <= data_evento_final_no_mes:
                            if (not periodo.dias_semana or
                                    datetime.date(int(ano), int(mes), i).weekday() in periodo.dias_semana):
                                append(i, periodo, inclusao)
                            i += 1
                    else:
                        append(inclusao.data_evento.day, periodo, inclusao)
        data = {
            'results': return_dict
        }

        return Response(data)

    @action(detail=False, methods=['GET'], url_path=f'{SUSPENSOES_AUTORIZADAS}')
    def suspensoes_autorizadas(self, request):
        escola_uuid = request.query_params.get('escola_uuid')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')
        nome_periodo_escolar = request.query_params.get('nome_periodo_escolar')

        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        query_set = query_set.filter(data_evento__month=mes, data_evento__year=ano)
        query_set = query_set.filter(data_evento__lt=datetime.date.today())
        query_set = self.remove_duplicados_do_query_set(query_set)
        return_dict = []

        for suspensao in query_set:
            susp = suspensao.get_raw_model.objects.get(uuid=suspensao.uuid)
            s_quant_periodo = susp.quantidades_por_periodo.get(periodo_escolar__nome=nome_periodo_escolar)
            if s_quant_periodo:
                tipos_alimentacao = s_quant_periodo.tipos_alimentacao.all()
                alimentacoes = [unicodedata.normalize('NFD', alimentacao.nome.replace(' ', '_')).encode(
                    'ascii', 'ignore').decode('utf-8').lower() for alimentacao in tipos_alimentacao]
                return_dict.append({
                    'dia': f'{susp.data.day:02d}',
                    'periodo': nome_periodo_escolar,
                    'alimentacoes': alimentacoes,
                    'numero_alunos': s_quant_periodo.numero_alunos,
                    'inclusao_id_externo': susp.id_externo
                })

        data = {
            'results': return_dict
        }

        return Response(data)

    def trata_lanche_emergencial_queryset(self, eh_lanche_emergencial, query_set):
        if eh_lanche_emergencial == 'true':
            query_set = query_set.filter(motivo__icontains='Emergencial')
        else:
            query_set = query_set.exclude(motivo__icontains='Emergencial')
        return query_set

    @action(detail=False, methods=['GET'], url_path=f'{ALTERACOES_ALIMENTACAO_AUTORIZADAS}')
    def alteracoes_alimentacoes_autorizadas(self, request):
        escola_uuid = request.query_params.get('escola_uuid')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')
        nome_periodo_escolar = request.query_params.get('nome_periodo_escolar')
        eh_lanche_emergencial = request.query_params.get('eh_lanche_emergencial', '')

        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        query_set = query_set.filter(data_evento__month=mes, data_evento__year=ano)
        query_set = query_set.filter(data_evento__lt=datetime.date.today())
        query_set = self.trata_lanche_emergencial_queryset(eh_lanche_emergencial, query_set)
        query_set = self.remove_duplicados_do_query_set(query_set)
        return_dict = []

        for alteracao_alimentacao in query_set:
            alteracao = alteracao_alimentacao.get_raw_model.objects.get(uuid=alteracao_alimentacao.uuid)
            if eh_lanche_emergencial == 'true':
                for data_evento in alteracao.datas_intervalo.filter(data__month=mes, data__year=ano):
                    return_dict.append({
                        'dia': f'{data_evento.data.day:02d}',
                        'numero_alunos': sum([sub.qtd_alunos for sub in alteracao.substituicoes_periodo_escolar.all()]),
                        'inclusao_id_externo': alteracao.id_externo,
                        'motivo': alteracao_alimentacao.motivo
                    })
            else:
                alt = alteracao.substituicoes_periodo_escolar.get(periodo_escolar__nome=nome_periodo_escolar)
                if alt:
                    for data_evento in alteracao.datas_intervalo.filter(data__month=mes, data__year=ano):
                        return_dict.append({
                            'dia': f'{data_evento.data.day:02d}',
                            'periodo': nome_periodo_escolar,
                            'numero_alunos': alt.qtd_alunos,
                            'inclusao_id_externo': alteracao.id_externo,
                            'motivo': alteracao_alimentacao.motivo
                        })

        data = {
            'results': return_dict
        }

        return Response(data)

    @action(detail=False, methods=['GET'], url_path=f'{KIT_LANCHES_AUTORIZADAS}')
    def kit_lanches_autorizadas(self, request):
        escola_uuid = request.query_params.get('escola_uuid')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')

        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        query_set = query_set.filter(data_evento__month=mes, data_evento__year=ano)
        query_set = query_set.filter(data_evento__lt=datetime.date.today())
        query_set = self.remove_duplicados_do_query_set(query_set)
        return_dict = []

        for kit_lanche in query_set:
            kit_lanche = kit_lanche.get_raw_model.objects.get(uuid=kit_lanche.uuid)
            if kit_lanche:
                return_dict.append({
                    'dia': f'{kit_lanche.solicitacao_kit_lanche.data.day:02d}',
                    'numero_alunos': kit_lanche.quantidade_alimentacoes,
                    'kit_lanche_id_externo': kit_lanche.id_externo,
                })

        data = {
            'results': return_dict
        }

        return Response(data)

    @action(detail=False, methods=['GET'], url_path=f'{INCLUSOES_ETEC_AUTORIZADAS}')
    def inclusoes_etec_autorizadas(self, request):
        escola_uuid = request.query_params.get('escola_uuid')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')
        date = datetime.date(int(ano), int(mes), 1)

        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        query_set = query_set.filter(
            Q(data_evento__month=mes, data_evento__year=ano) |
            Q(data_evento__lt=date, data_evento_2__gte=date)
        )
        query_set = query_set.filter(
            data_evento__lt=datetime.date.today(),
            motivo='ETEC'
        )
        query_set = self.remove_duplicados_do_query_set(query_set)

        return_dict = []

        def append(dia, inclusao):
            resultado = formata_resultado_inclusoes_etec_autorizadas(dia, mes, ano, inclusao)
            return_dict.append(resultado) if resultado else None

        for sol_escola in query_set:
            inclusao = sol_escola.get_raw_model.objects.get(uuid=sol_escola.uuid)
            dia = sol_escola.data_evento.day
            big_range = False
            data_evento_final_no_mes = None
            if sol_escola.data_evento.month != int(mes) and sol_escola.data_evento_2.month != int(mes):
                big_range = True
                i = datetime.date(int(ano), int(mes), 1)
                data_evento_final_no_mes = (i + relativedelta(day=31)).day
                dia = datetime.date(int(ano), int(mes), 1).day
            elif sol_escola.data_evento.month != int(mes):
                big_range = True
                data_evento_final_no_mes = sol_escola.data_evento_2.day
                dia = datetime.date(int(ano), int(mes), 1).day
            else:
                data_evento_final_no_mes = sol_escola.data_evento_2.day
            data_evento_final_no_mes = tratar_data_evento_final_no_mes(data_evento_final_no_mes, sol_escola, big_range)
            while dia <= data_evento_final_no_mes:
                append(dia, inclusao)
                dia += 1
        data = {
            'results': tratar_dias_duplicados(return_dict)
        }

        return Response(data)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}')
    def negados(self, request):
        escola_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesEscola.get_negados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}')
    def cancelados(self, request):
        escola_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesEscola.get_cancelados(escola_uuid=escola_uuid)
        query_set = SolicitacoesEscola.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{RESUMO_ANO}')
    def evolucao_solicitacoes(self, request):
        usuario = request.user
        escola_uuid = usuario.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesEscola.get_solicitacoes_ano_corrente(
            escola_uuid=escola_uuid)
        response = {'results': self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)}
        return Response(response)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RESUMO_MES}')
    def resumo_mes(self, request):
        usuario = request.user
        escola_uuid = usuario.vinculo_atual.instituicao.uuid
        totais_dict = SolicitacoesEscola.resumo_totais_mes(
            escola_uuid=escola_uuid,
        )
        return Response(totais_dict)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_RESUMO_MES_ANO}',
    )
    def relatorio_resumo_anual_e_mensal(self, request):
        usuario = request.user
        escola_uuid = usuario.vinculo_atual.instituicao.uuid

        query_set = SolicitacoesEscola.get_solicitacoes_ano_corrente(
            escola_uuid=escola_uuid)
        resumo_do_ano = self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)
        resumo_do_mes = SolicitacoesEscola.resumo_totais_mes(
            escola_uuid=escola_uuid,
        )
        return relatorio_resumo_anual_e_mensal(request, resumo_do_mes, resumo_do_ano)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_PERIODO}',
    )
    def relatorio_filtro_periodo(self, request):
        usuario = request.user
        escola = usuario.vinculo_atual.instituicao
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesEscola.filtros_escola(
                escola_uuid=escola.uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            query_set = self.remove_duplicados_do_query_set(query_set)

            return relatorio_filtro_periodo(request, query_set, escola.nome, escola.diretoria_regional.nome)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{PESQUISA}')
    def filtro_periodo_tipo_solicitacao(self, request):
        """Filtro de todas as solicitações da escola.

        ---
        tipo_solicitacao -- ALT_CARDAPIO|INV_CARDAPIO|INC_ALIMENTA|INC_ALIMENTA_CONTINUA|
        KIT_LANCHE_AVULSA|SUSP_ALIMENTACAO|KIT_LANCHE_UNIFICADA|TODOS
        status_solicitacao -- AUTORIZADOS|NEGADOS|CANCELADOS|RECEBIDAS|TODOS
        data_inicial -- dd-mm-yyyy
        data_final -- dd-mm-yyyy
        """
        usuario = request.user
        escola_uuid = usuario.vinculo_atual.instituicao.uuid
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesEscola.filtros_escola(
                escola_uuid=escola_uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            return self._retorno_base(query_set)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def filtrar_solicitacoes_para_relatorio(self, request):
        escola_uuid = request.user.vinculo_atual.instituicao.uuid
        status = request.query_params.get('status', None)
        queryset = SolicitacoesEscola.map_queryset_por_status(status, escola_uuid=escola_uuid)
        # filtra por datas
        periodo_datas = {
            'data_evento': request.query_params.get('de', None),
            'data_evento_fim': request.query_params.get('ate', None)
        }
        queryset = SolicitacoesEscola.busca_periodo_de_datas(queryset, periodo_datas)

        tipo_doc = request.query_params.getlist('tipos_solicitacao[]', None)
        tipo_doc = SolicitacoesEscola.map_queryset_por_tipo_doc(tipo_doc)
        # outros filtros
        map_filtros = {
            'lote_uuid__in': request.query_params.getlist('lotes[]', None),
            'escola_uuid__in': request.query_params.getlist('unidades_educacionais[]', None),
            'terceirizada_uuid': request.query_params.get('terceirizada', None),
            'tipo_doc__in': tipo_doc,
            'escola_tipo_unidade_uuid__in': request.query_params.getlist('tipos_unidade[]', None),
        }
        filtros = {key: value for key, value in map_filtros.items() if value not in [None, []]}
        queryset = queryset.filter(**filtros).order_by('lote_nome', 'escola_nome', 'terceirizada_nome')
        return queryset

    @action(detail=False,
            methods=['GET'],
            url_path='filtrar-solicitacoes-ga',
            permission_classes=(UsuarioEscolaTercTotal,))
    def filtrar_solicitacoes_ga(self, request):
        # queryset por status
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        return self._retorno_base(queryset, False)

    @action(detail=False, methods=['GET'], url_path='exportar-xlsx')
    def exportar_xlsx(self, request):
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        lotes = request.query_params.getlist('lotes[]')
        tipos_solicitacao = request.query_params.getlist('tipos_solicitacao[]')
        tipos_unidade = request.query_params.getlist('tipos_unidade[]')
        unidades_educacionais = request.query_params.getlist('unidades_educacionais[]')

        user = request.user.get_username()
        gera_xls_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.xlsx',
            data=self.request.query_params,
            uuids=uuids,
            lotes=lotes,
            tipos_solicitacao=tipos_solicitacao,
            tipos_unidade=tipos_unidade,
            unidades_educacionais=unidades_educacionais
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        user = request.user.get_username()
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        gera_pdf_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.pdf',
            data=self.request.query_params,
            uuids=uuids,
            status=request.query_params.get('status', None)
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)


class DRESolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesDRE.objects.all()
    permission_classes = (UsuarioDiretoriaRegional,)
    serializer_class = SolicitacoesSerializer

    @action(detail=False,
            methods=['GET'],
            url_path=f'{PENDENTES_VALIDACAO_DRE}/{FILTRO_PADRAO_PEDIDOS}/{TIPO_VISAO}')
    def pendentes_validacao(self, request, filtro_aplicado=SEM_FILTRO, tipo_visao=TIPO_VISAO_SOLICITACOES):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_pendentes_validacao(dre_uuid=diretoria_regional.uuid,
                                                            filtro=filtro_aplicado)
        query_set = SolicitacoesDRE.busca_filtro(query_set, request.query_params)
        response = {'results': self._agrupa_por_tipo_visao(
            tipo_visao=tipo_visao, query_set=query_set)}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def pendentes_autorizacao_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_pendentes_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def autorizados_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_autorizados_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def negados_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_negados_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def cancelados_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_cancelados_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def autorizadas_temporariamente_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_autorizadas_temporariamente_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{INATIVAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}')
    def inativas_temporariamente_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_inativas_temporariamente_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{INATIVAS_DIETA_ESPECIAL}/{FILTRO_DRE_UUID}',
            permission_classes=(IsAuthenticated, PermissaoParaRecuperarDietaEspecial,))
    def inativas_dieta_especial(self, request, dre_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesDRE.get_inativas_dieta_especial(
            dre_uuid=dre_uuid)
        query_set = SolicitacoesDRE.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO}')
    def pendentes_autorizacao(self, request, dre_uuid=None):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_pendentes_validacao(dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}')
    def autorizados(self, request, dre_uuid=None):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_autorizados(
            dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AGUARDANDO_CODAE}')
    def aguardando_codae(self, request, dre_uuid=None):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_aguardando_codae(
            dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesDRE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}')
    def negados(self, request, dre_uuid=None):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_negados(
            dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}')
    def cancelados(self, request, dre_uuid=None):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        query_set = SolicitacoesDRE.get_cancelados(
            dre_uuid=diretoria_regional.uuid)
        query_set = SolicitacoesCODAE.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RESUMO_MES}')
    def resumo_mes(self, request):
        usuario = request.user
        dre_uuid = usuario.vinculo_atual.instituicao.uuid
        totais_dict = SolicitacoesDRE.resumo_totais_mes(
            dre_uuid=dre_uuid,
        )
        return Response(totais_dict)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_RESUMO_MES_ANO}',
    )
    def relatorio_resumo_anual_e_mensal(self, request):
        usuario = request.user
        dre_uuid = usuario.vinculo_atual.instituicao.uuid

        query_set = SolicitacoesDRE.get_solicitacoes_ano_corrente(
            dre_uuid=dre_uuid)
        resumo_do_ano = self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)
        resumo_do_mes = SolicitacoesDRE.resumo_totais_mes(
            dre_uuid=dre_uuid,
        )
        return relatorio_resumo_anual_e_mensal(request, resumo_do_mes, resumo_do_ano)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{RELATORIO_PERIODO}/{FILTRO_ESCOLA_UUID}',
    )
    def relatorio_filtro_periodo(self, request, escola_uuid=None):
        usuario = request.user
        dre = usuario.vinculo_atual.instituicao
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesDRE.filtros_dre(
                escola_uuid=escola_uuid,
                dre_uuid=dre.uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            query_set = self.remove_duplicados_do_query_set(query_set)

            return relatorio_filtro_periodo(request, query_set, dre.nome, escola_uuid)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path=f'{RESUMO_ANO}')
    def evolucao_solicitacoes(self, request):
        usuario = request.user
        dre_uuid = usuario.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesDRE.get_solicitacoes_ano_corrente(
            dre_uuid=dre_uuid)
        response = {'results': self._agrupa_por_mes_por_solicitacao(
            query_set=query_set)}
        return Response(response)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{PESQUISA}/{FILTRO_ESCOLA_UUID}')
    def filtro_periodo_tipo_solicitacao(self, request, escola_uuid=None):
        """Filtro de todas as solicitações da dre.

        ---
        tipo_solicitacao -- ALT_CARDAPIO|INV_CARDAPIO|INC_ALIMENTA|INC_ALIMENTA_CONTINUA|
        KIT_LANCHE_AVULSA|SUSP_ALIMENTACAO|KIT_LANCHE_UNIFICADA|TODOS
        status_solicitacao -- AUTORIZADOS|NEGADOS|CANCELADOS|RECEBIDAS|TODOS
        data_inicial -- dd-mm-yyyy
        data_final -- dd-mm-yyyy
        """
        usuario = request.user
        dre_uuid = usuario.vinculo_atual.instituicao.uuid
        form = FiltroValidator(request.GET)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            query_set = SolicitacoesDRE.filtros_dre(
                escola_uuid=escola_uuid,
                dre_uuid=dre_uuid,
                data_inicial=cleaned_data.get('data_inicial'),
                data_final=cleaned_data.get('data_final'),
                tipo_solicitacao=cleaned_data.get('tipo_solicitacao'),
                status_solicitacao=cleaned_data.get('status_solicitacao')
            )
            return self._retorno_base(query_set)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def filtrar_solicitacoes_para_relatorio(self, request):
        dre_uuid = request.user.vinculo_atual.instituicao.uuid
        status = request.query_params.get('status', None)
        queryset = SolicitacoesDRE.map_queryset_por_status(status, dre_uuid=dre_uuid)
        # filtra por datas
        periodo_datas = {
            'data_evento': request.query_params.get('de', None),
            'data_evento_fim': request.query_params.get('ate', None)
        }
        queryset = SolicitacoesDRE.busca_periodo_de_datas(queryset, periodo_datas)

        tipo_doc = request.query_params.getlist('tipos_solicitacao[]', None)
        tipo_doc = SolicitacoesDRE.map_queryset_por_tipo_doc(tipo_doc)
        # outros filtros
        map_filtros = {
            'lote_uuid__in': request.query_params.getlist('lotes[]', None),
            'escola_uuid__in': request.query_params.getlist('unidades_educacionais[]', None),
            'terceirizada_uuid': request.query_params.get('terceirizada', None),
            'tipo_doc__in': tipo_doc,
            'escola_tipo_unidade_uuid__in': request.query_params.getlist('tipos_unidade[]', None),
        }
        filtros = {key: value for key, value in map_filtros.items() if value not in [None, []]}
        queryset = queryset.filter(**filtros).order_by('lote_nome', 'escola_nome', 'terceirizada_nome')
        return queryset

    @action(detail=False,
            methods=['GET'],
            url_path='filtrar-solicitacoes-ga',
            permission_classes=(UsuarioDiretoriaRegional,))
    def filtrar_solicitacoes_ga(self, request):
        # queryset por status
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        return self._retorno_base(queryset, False)

    @action(detail=False, methods=['GET'], url_path='exportar-xlsx')
    def exportar_xlsx(self, request):
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        lotes = request.query_params.getlist('lotes[]')
        tipos_solicitacao = request.query_params.getlist('tipos_solicitacao[]')
        tipos_unidade = request.query_params.getlist('tipos_unidade[]')
        unidades_educacionais = request.query_params.getlist('unidades_educacionais[]')

        user = request.user.get_username()
        gera_xls_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.xlsx',
            data=self.request.query_params,
            uuids=uuids,
            lotes=lotes,
            tipos_solicitacao=tipos_solicitacao,
            tipos_unidade=tipos_unidade,
            unidades_educacionais=unidades_educacionais
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        user = request.user.get_username()
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        gera_pdf_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.pdf',
            data=self.request.query_params,
            uuids=uuids,
            status=request.query_params.get('status', None)
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)


class TerceirizadaSolicitacoesViewSet(SolicitacoesViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesTerceirizada.objects.all()
    permission_classes = (UsuarioTerceirizada,)
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'],
            url_path=f'{PENDENTES_AUTORIZACAO_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}')
    def pendentes_autorizacao_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_pendentes_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}')
    def autorizados_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_autorizados_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}')
    def negados_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_negados_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}')
    def cancelados_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_cancelados_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{AUTORIZADAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}'
    )
    def autorizadas_temporariamente_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_autorizadas_temporariamente_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{AGUARDANDO_INICIO_VIGENCIA_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}')
    def aguardando_inicio_vigencia_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_aguardando_vigencia_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(
        detail=False,
        methods=['GET'],
        url_path=f'{INATIVAS_TEMPORARIAMENTE_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}'
    )
    def inativas_temporariamente_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_inativas_temporariamente_dieta_especial(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False,
            methods=['GET'],
            url_path=f'{INATIVAS_DIETA_ESPECIAL}/{FILTRO_TERCEIRIZADA_UUID}',
            )
    def inativas_dieta_especial(self, request, terceirizada_uuid=None):
        tem_parametro_sem_paginacao = request.GET.get('sem_paginacao', False)
        query_set = SolicitacoesTerceirizada.get_inativas_dieta_especial(terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro_dietas_especiais(query_set, request.query_params)
        if tem_parametro_sem_paginacao:
            return self._retorno_base(query_set, True)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{QUESTIONAMENTOS}')
    def questionamentos(self, request):
        terceirizada_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesTerceirizada.get_questionamentos(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO}/{FILTRO_TERCEIRIZADA_UUID}')
    def pendentes_autorizacao(self, request, terceirizada_uuid=None):
        query_set = SolicitacoesTerceirizada.get_pendentes_autorizacao(
            terceirizada_uuid=terceirizada_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}')
    def autorizados(self, request):
        terceirizada_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesTerceirizada.get_autorizados(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}')
    def negados(self, request):
        terceirizada_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesTerceirizada.get_negados(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}')
    def cancelados(self, request):
        terceirizada_uuid = request.user.vinculo_atual.instituicao.uuid
        query_set = SolicitacoesTerceirizada.get_cancelados(
            terceirizada_uuid=terceirizada_uuid)
        query_set = SolicitacoesTerceirizada.busca_filtro(query_set, request.query_params)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'],
            url_path=f'{PENDENTES_CIENCIA}/{FILTRO_TERCEIRIZADA_UUID}/{FILTRO_PADRAO_PEDIDOS}/{TIPO_VISAO}')
    def pendentes_ciencia(self, request, terceirizada_uuid=None, filtro_aplicado=SEM_FILTRO,
                          tipo_visao=TIPO_VISAO_SOLICITACOES):
        query_set = SolicitacoesTerceirizada.get_pendentes_ciencia(terceirizada_uuid=terceirizada_uuid,
                                                                   filtro=filtro_aplicado)
        response = {'results': self._agrupa_por_tipo_visao(
            tipo_visao=tipo_visao, query_set=query_set)}
        return Response(response)

    def filtrar_solicitacoes_para_relatorio(self, request):
        terceirizada_uuid = request.user.vinculo_atual.instituicao.uuid
        status = request.query_params.get('status', None)
        queryset = SolicitacoesTerceirizada.map_queryset_por_status(status, terceirizada_uuid=terceirizada_uuid)
        # filtra por datas
        periodo_datas = {
            'data_evento': request.query_params.get('de', None),
            'data_evento_fim': request.query_params.get('ate', None)
        }
        queryset = SolicitacoesTerceirizada.busca_periodo_de_datas(queryset, periodo_datas)

        tipo_doc = request.query_params.getlist('tipos_solicitacao[]', None)
        tipo_doc = SolicitacoesTerceirizada.map_queryset_por_tipo_doc(tipo_doc)
        # outros filtros
        map_filtros = {
            'lote_uuid__in': request.query_params.getlist('lotes[]', None),
            'escola_uuid__in': request.query_params.getlist('unidades_educacionais[]', None),
            'terceirizada_uuid': request.query_params.get('terceirizada', None),
            'tipo_doc__in': tipo_doc,
            'escola_tipo_unidade_uuid__in': request.query_params.getlist('tipos_unidade[]', None),
        }
        filtros = {key: value for key, value in map_filtros.items() if value not in [None, []]}
        queryset = queryset.filter(**filtros).order_by('lote_nome', 'escola_nome', 'terceirizada_nome')
        return queryset

    @action(detail=False,
            methods=['GET'],
            url_path='filtrar-solicitacoes-ga',
            permission_classes=(UsuarioTerceirizada,))
    def filtrar_solicitacoes_ga(self, request):
        # queryset por status
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        return self._retorno_base(queryset, False)

    @action(detail=False, methods=['GET'], url_path='exportar-xlsx')
    def exportar_xlsx(self, request):
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        lotes = request.query_params.getlist('lotes[]')
        tipos_solicitacao = request.query_params.getlist('tipos_solicitacao[]')
        tipos_unidade = request.query_params.getlist('tipos_unidade[]')
        unidades_educacionais = request.query_params.getlist('unidades_educacionais[]')

        user = request.user.get_username()
        gera_xls_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.xlsx',
            data=self.request.query_params,
            uuids=uuids,
            lotes=lotes,
            tipos_solicitacao=tipos_solicitacao,
            tipos_unidade=tipos_unidade,
            unidades_educacionais=unidades_educacionais
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        user = request.user.get_username()
        queryset = self.filtrar_solicitacoes_para_relatorio(request)
        uuids = [str(solicitacao.uuid) for solicitacao in queryset]
        gera_pdf_relatorio_solicitacoes_alimentacao_async.delay(
            user=user,
            nome_arquivo='relatorio_solicitacoes_alimentacao.pdf',
            data=self.request.query_params,
            uuids=uuids,
            status=request.query_params.get('status', None)
        )
        return Response(dict(detail='Solicitação de geração de arquivo recebida com sucesso.'),
                        status=status.HTTP_200_OK)


class DietaEspecialSolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()
    serializer_class = SolicitacaoDietaEspecialSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_AUTORIZACAO}')
    def pendentes_autorizacao(self, request):
        return self._retorno_base(DietaEspecialWorkflow.CODAE_A_AUTORIZAR)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}')
    def autorizados(self, request):
        return self._retorno_base(DietaEspecialWorkflow.CODAE_AUTORIZADO)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}')
    def negados(self, request):
        return self._retorno_base(DietaEspecialWorkflow.CODAE_NEGOU_PEDIDO)

    def _retorno_base(self, status):
        query_set = self.queryset.filter(status=status)
        page = self.paginate_queryset(query_set)
        serializer = SolicitacaoDietaEspecialLogSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
