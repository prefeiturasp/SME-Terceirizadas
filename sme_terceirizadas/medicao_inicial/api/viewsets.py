from calendar import monthrange
from django.db.models import QuerySet, Sum
from django.template.loader import render_to_string
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ...dados_comuns.models import LogSolicitacoesUsuario
from ...dados_comuns.permissions import (
    UsuarioCODAEGestaoAlimentacao,
    UsuarioDiretoriaRegional,
    UsuarioEscola,
    ViewSetActionPermissionMixin
)
from ...dieta_especial.models import LogQuantidadeDietasAutorizadas
from ...escola.api.permissions import PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada
from ...escola.models import Escola, LogAlunosMatriculadosPeriodoEscola
from ..models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    Medicao,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from .permissions import EhAdministradorMedicaoInicialOuGestaoAlimentacao
from .serializers import (
    CategoriaMedicaoSerializer,
    DiaSobremesaDoceSerializer,
    SolicitacaoMedicaoInicialDashboardSerializer,
    SolicitacaoMedicaoInicialSerializer,
    TipoContagemAlimentacaoSerializer,
    ValorMedicaoSerializer
)
from .serializers_create import (
    DiaSobremesaDoceCreateManySerializer,
    MedicaoCreateUpdateSerializer,
    SolicitacaoMedicaoInicialCreateSerializer
)
from ...relatorios.utils import html_to_pdf_file


class DiaSobremesaDoceViewSet(ViewSetActionPermissionMixin, ModelViewSet):
    permission_action_classes = {
        'list': [EhAdministradorMedicaoInicialOuGestaoAlimentacao],
        'create': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada],
        'delete': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada]
    }
    queryset = DiaSobremesaDoce.objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaSobremesaDoceCreateManySerializer
        return DiaSobremesaDoceSerializer

    def get_queryset(self):
        queryset = DiaSobremesaDoce.objects.all()
        if 'mes' in self.request.query_params and 'ano' in self.request.query_params:
            queryset = queryset.filter(data__month=self.request.query_params.get('mes'),
                                       data__year=self.request.query_params.get('ano'))
        if 'escola_uuid' in self.request.query_params:
            escola = Escola.objects.get(uuid=self.request.query_params.get('escola_uuid'))
            queryset = queryset.filter(tipo_unidade=escola.tipo_unidade)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super(DiaSobremesaDoceViewSet, self).create(request, *args, **kwargs)
        except AssertionError as error:
            if str(error) == '`create()` did not return an object instance.':
                return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path='lista-dias')
    def lista_dias(self, request):
        try:
            lista_dias = self.get_queryset().values_list('data', flat=True).distinct()
            return Response(lista_dias, status=status.HTTP_200_OK)
        except Escola.DoesNotExist as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SolicitacaoMedicaoInicialViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [UsuarioEscola | UsuarioDiretoriaRegional]
    queryset = SolicitacaoMedicaoInicial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoMedicaoInicialCreateSerializer
        return SolicitacaoMedicaoInicialSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        escola_uuid = request.query_params.get('escola')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')

        queryset = queryset.filter(escola__uuid=escola_uuid, mes=mes, ano=ano)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def get_lista_status():
        return [
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_ENVIADA_PELA_UE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA_CODAE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRIGIDA_PELA_UE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_DRE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_CODAE,
            'TODOS_OS_LANCAMENTOS'
        ]

    def condicao_raw_query_por_usuario(self):
        usuario = self.request.user
        if usuario.tipo_usuario == 'diretoriaregional':
            return f'AND diretoria_regional_id = {self.request.user.vinculo_atual.object_id} '
        elif usuario.tipo_usuario == 'escola':
            return f'AND %(solicitacao_medicao_inicial)s.escola_id = {self.request.user.vinculo_atual.object_id} '
        return ''

    def condicao_por_usuario(self, queryset):
        usuario = self.request.user
        if usuario.tipo_usuario == 'diretoriaregional':
            return queryset.filter(escola__diretoria_regional=usuario.vinculo_atual.instituicao)
        elif usuario.tipo_usuario == 'escola':
            return queryset.filter(escola=usuario.vinculo_atual.instituicao)
        return queryset

    def dados_dashboard(self, request, query_set: QuerySet, kwargs: dict, use_raw=True) -> list:
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))

        sumario = []
        for workflow in self.get_lista_status():
            todos_lancamentos = workflow == 'TODOS_OS_LANCAMENTOS'
            if use_raw:
                data = {'escola': Escola._meta.db_table,
                        'logs': LogSolicitacoesUsuario._meta.db_table,
                        'solicitacao_medicao_inicial': SolicitacaoMedicaoInicial._meta.db_table,
                        'status': workflow}
                raw_sql = ('SELECT %(solicitacao_medicao_inicial)s.* FROM %(solicitacao_medicao_inicial)s '
                           'JOIN (SELECT uuid_original, MAX(criado_em) AS log_criado_em FROM %(logs)s '
                           'GROUP BY uuid_original) '
                           'AS most_recent_log '
                           'ON %(solicitacao_medicao_inicial)s.uuid = most_recent_log.uuid_original '
                           'LEFT JOIN (SELECT id AS escola_id, diretoria_regional_id FROM %(escola)s) '
                           'AS escola_solicitacao_medicao '
                           'ON escola_solicitacao_medicao.escola_id = %(solicitacao_medicao_inicial)s.escola_id ')
                if todos_lancamentos:
                    raw_sql += ('WHERE NOT %(solicitacao_medicao_inicial)s.status = '
                                "'MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE' ")
                else:
                    raw_sql += "WHERE %(solicitacao_medicao_inicial)s.status = '%(status)s' "
                raw_sql += self.condicao_raw_query_por_usuario()
                raw_sql += 'ORDER BY log_criado_em DESC'
                qs = query_set.raw(raw_sql % data)
            else:
                qs = (query_set.filter(status=workflow) if not todos_lancamentos
                      else query_set.exclude(status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE'))
                qs = qs.filter(**kwargs)
                qs = self.condicao_por_usuario(qs)
                qs = sorted(qs.distinct().all(),
                            key=lambda x: x.log_mais_recente.criado_em
                            if x.log_mais_recente else '-criado_em', reverse=True)
            sumario.append({
                'status': workflow,
                'total': len(qs),
                'dados': SolicitacaoMedicaoInicialDashboardSerializer(
                    qs[offset:limit + offset],
                    context={'request': self.request, 'workflow': workflow}, many=True).data
            })
        return sumario

    def formatar_filtros(self, query_params):
        kwargs = {}
        if query_params.get('mes_ano'):
            data_splitted = query_params.get('mes_ano').split('_')
            kwargs['mes'] = data_splitted[0]
            kwargs['ano'] = data_splitted[1]
        if query_params.getlist('lotes_selecionados[]'):
            kwargs['escola__lote__uuid__in'] = query_params.getlist('lotes_selecionados[]')
        if query_params.get('tipo_unidade'):
            kwargs['escola__tipo_unidade__uuid'] = query_params.get('tipo_unidade')
        if query_params.get('escola'):
            kwargs['escola__codigo_eol'] = query_params.get('escola').split(' - ')[0]
        if query_params.get('dre'):
            kwargs['escola__diretoria_regional__uuid'] = query_params.get('dre')
        return kwargs

    @action(detail=False, methods=['GET'], url_path='dashboard',
            permission_classes=[UsuarioEscola | UsuarioDiretoriaRegional | UsuarioCODAEGestaoAlimentacao])
    def dashboard(self, request):
        query_set = self.get_queryset()
        possui_filtros = len(request.query_params)
        kwargs = self.formatar_filtros(request.query_params)
        response = {'results': self.dados_dashboard(query_set=query_set,
                                                    request=request,
                                                    kwargs=kwargs,
                                                    use_raw=not possui_filtros)}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='meses-anos',
            permission_classes=[UsuarioEscola | UsuarioDiretoriaRegional | UsuarioCODAEGestaoAlimentacao])
    def meses_anos(self, request):
        query_set = self.condicao_por_usuario(self.get_queryset()).exclude(
            status=SolicitacaoMedicaoInicial.workflow_class.MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE)
        meses_anos = query_set.values_list('mes', 'ano')
        meses_anos_unicos = []
        for mes_ano in meses_anos:
            mes_ano_obj = {'mes': mes_ano[0], 'ano': mes_ano[1]}
            if mes_ano_obj not in meses_anos_unicos:
                meses_anos_unicos.append(mes_ano_obj)
        return Response({'results': sorted(meses_anos_unicos, key=lambda k: (k['ano'], k['mes']), reverse=True)},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='relatorio-pdf')
    def relatorio_pdf(self, request, uuid):
        solicitacao = self.get_object()
        tabelas = [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_categorias': [], 'valores_campos': []}]
        MAX_COLUNAS = 15
        CATEGORIA = 0
        CAMPO = 1
        indice_atual = 0
        ORDEM_CAMPOS = {
            'matriculados': -1,
            'aprovadas': 0,
            'frequencia': 1,
            'solicitado': 2,
            'desjejum': 3,
            'lanche': 4,
            'refeicao': 5,
            'repeticao_refeicao': 6,
            'lanche_emergencial': 7,
            'total_refeicoes_pagamento': 8,
            'sobremesa': 9,
            'repeticao_sobremesa': 10,
            'total_sobremesas_pagamento': 11
        }
        for medicao in solicitacao.medicoes.all():
            lista_categorias_campos = sorted(list(
                medicao.valores_medicao.values_list('categoria_medicao__nome', 'nome_campo').distinct()))
            dict_categorias_campos = {}
            for categoria_campo in lista_categorias_campos:
                if categoria_campo[CATEGORIA] not in dict_categorias_campos.keys():
                    if 'DIETA' in categoria_campo[CATEGORIA]:
                        dict_categorias_campos[categoria_campo[CATEGORIA]] = ['aprovadas']
                    else:
                        dict_categorias_campos[categoria_campo[CATEGORIA]] = [
                            'matriculados', 'total_refeicoes_pagamento', 'total_sobremesas_pagamento']
                    dict_categorias_campos[categoria_campo[CATEGORIA]] += [categoria_campo[CAMPO]]
                else:
                    dict_categorias_campos[categoria_campo[CATEGORIA]] += [categoria_campo[CAMPO]]
            for categoria in dict_categorias_campos.keys():
                if len(tabelas[indice_atual]['nomes_campos']) + len(dict_categorias_campos[categoria]) <= MAX_COLUNAS:
                    if medicao.periodo_escolar.nome not in tabelas[indice_atual]['periodos']:
                        tabelas[indice_atual]['periodos'] += [medicao.periodo_escolar.nome]
                    tabelas[indice_atual]['categorias'] += [categoria]
                    tabelas[indice_atual]['nomes_campos'] += sorted(
                        dict_categorias_campos[categoria], key=lambda k: ORDEM_CAMPOS[k])
                    tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
                else:
                    indice_atual += 1
                    tabelas += [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_categorias': [],
                                 'valores_campos': []}]
                    tabelas[indice_atual]['periodos'] += [medicao.periodo_escolar.nome]
                    tabelas[indice_atual]['categorias'] += [categoria]
                    tabelas[indice_atual]['nomes_campos'] += dict_categorias_campos[categoria]
                    tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
        dias_no_mes = range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1)

        logs_alunos_matriculados = LogAlunosMatriculadosPeriodoEscola.objects.filter(
            escola=solicitacao.escola, criado_em__month=solicitacao.mes, criado_em__year=solicitacao.ano)
        logs_dietas = LogQuantidadeDietasAutorizadas.objects.filter(
            escola=solicitacao.escola, data__month=solicitacao.mes, data__year=solicitacao.ano)
        for indice_tabela in range(0, len(tabelas)):
            tabela = tabelas[indice_tabela]
            for dia in dias_no_mes:
                valores_dia = [dia]
                indice_campo = 0
                indice_categoria = 0
                categoria_corrente = tabela['categorias'][indice_categoria]
                for campo in tabela['nomes_campos']:
                    if indice_campo > tabela['len_categorias'][indice_categoria] - 1:
                        indice_campo = 0
                        indice_categoria += 1
                        categoria_corrente = tabela['categorias'][indice_categoria]
                    if campo == 'matriculados':
                        try:
                            valores_dia += [logs_alunos_matriculados.get(criado_em__day=dia).quantidade_alunos]
                        except LogAlunosMatriculadosPeriodoEscola.DoesNotExist:
                            valores_dia += ['-']
                    elif campo == 'aprovadas':
                        try:
                            if 'ENTERAL' in categoria_corrente:
                                quantidade = logs_dietas.filter(
                                    data__day=dia,
                                    data__month=solicitacao.mes,
                                    data__year=solicitacao.ano,
                                    classificacao__nome__in=[
                                        'Tipo A RESTRIÇÃO DE AMINOÁCIDOS',
                                        'Tipo A ENTERAL'
                                    ]).aggregate(Sum('quantidade')).get('quantidade__sum')
                                valores_dia += [quantidade]
                            else:
                                valores_dia += [logs_dietas.get(
                                    data__day=dia,
                                    data__month=solicitacao.mes,
                                    data__year=solicitacao.ano,
                                    classificacao__nome=categoria_corrente.split(' - ')[1].title()
                                ).quantidade]
                        except LogQuantidadeDietasAutorizadas.DoesNotExist:
                            valores_dia += ['-']
                    else:
                        valores_dia += ['-']
                    indice_campo += 1
                tabela['valores_campos'] += [valores_dia]
        html_string = render_to_string(
            f'relatorio_solicitacao_medicao_por_escola.html',
            {
                'solicitacao': solicitacao,
                'quantidade_dias_mes': range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1),
                'tabelas': tabelas
            }
        )
        return html_to_pdf_file(html_string, f'relatorio_dieta_especial.pdf')


class TipoContagemAlimentacaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = TipoContagemAlimentacao.objects.filter(ativo=True)
    serializer_class = TipoContagemAlimentacaoSerializer
    pagination_class = None


class CategoriaMedicaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = CategoriaMedicao.objects.filter(ativo=True)
    serializer_class = CategoriaMedicaoSerializer
    pagination_class = None


class ValorMedicaoViewSet(
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = ValorMedicao.objects.all()
    serializer_class = ValorMedicaoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ValorMedicao.objects.all()
        nome_periodo_escolar = self.request.query_params.get('nome_periodo_escolar', '')
        uuid_solicitacao_medicao = self.request.query_params.get('uuid_solicitacao_medicao', '')
        nome_grupo = self.request.query_params.get('nome_grupo', None)
        if nome_periodo_escolar:
            queryset = queryset.filter(medicao__periodo_escolar__nome=nome_periodo_escolar)
        if nome_grupo:
            queryset = queryset.filter(medicao__grupo__nome=nome_grupo)
        else:
            queryset = queryset.filter(medicao__grupo__isnull=True)
        if uuid_solicitacao_medicao:
            queryset = queryset.filter(medicao__solicitacao_medicao_inicial__uuid=uuid_solicitacao_medicao)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = ValorMedicao.objects.get(uuid=kwargs.get('uuid'))
        medicao = instance.medicao
        self.perform_destroy(instance)
        if not medicao.valores_medicao.all().exists():
            medicao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MedicaoViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = Medicao.objects.all()

    def get_serializer_class(self):
        return MedicaoCreateUpdateSerializer
