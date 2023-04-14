from calendar import monthrange

from django.db.models import Sum

from sme_terceirizadas.dieta_especial.models import LogQuantidadeDietasAutorizadas
from sme_terceirizadas.escola.models import LogAlunosMatriculadosPeriodoEscola
from sme_terceirizadas.medicao_inicial.models import GrupoMedicao, ValorMedicao


def build_dict_relacao_categorias_e_campos(medicao):
    CATEGORIA = 0
    CAMPO = 1

    lista_categorias_campos = sorted(list(
        medicao.valores_medicao.exclude(
            nome_campo__in=['observacoes', 'dietas_autorizadas', 'matriculados']
        ).values_list('categoria_medicao__nome', 'nome_campo').distinct()))
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
    return dict_categorias_campos


def get_tamanho_colunas_periodos(tabelas):
    for tabela in tabelas:
        if len(tabela['periodos']) == 1:
            tabela['len_periodos'] = [len(tabela['nomes_campos'])]
        else:
            indice_matriculados = next((i for i, categoria in enumerate(tabela['categorias'])
                                        if categoria == 'ALIMENTAÇÃO'), -1)
            tabela['len_periodos'] = [sum(tabela['len_categorias'][:indice_matriculados]),
                                      sum(tabela['len_categorias'][indice_matriculados:])]


def build_headers_tabelas(solicitacao):
    MAX_COLUNAS = 15
    ORDEM_CAMPOS = {
        'matriculados': -1,
        'aprovadas': 0,
        'frequencia': 1,
        'solicitado': 2,
        'desjejum': 3,
        'lanche': 4,
        'lanche_4h': 5,
        'refeicao': 6,
        'repeticao_refeicao': 7,
        'lanche_emergencial': 8,
        'total_refeicoes_pagamento': 9,
        'sobremesa': 10,
        'repeticao_sobremesa': 11,
        'total_sobremesas_pagamento': 12
    }

    tabelas = [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [], 'len_categorias': [],
                'valores_campos': []}]

    indice_atual = 0
    for medicao in solicitacao.medicoes.all():
        dict_categorias_campos = build_dict_relacao_categorias_e_campos(medicao)
        for categoria in dict_categorias_campos.keys():
            nome_periodo = (medicao.periodo_escolar.nome
                            if not medicao.grupo
                            else medicao.grupo.nome + ' - ' + medicao.periodo_escolar.nome)
            if len(tabelas[indice_atual]['nomes_campos']) + len(dict_categorias_campos[categoria]) <= MAX_COLUNAS:
                if nome_periodo not in tabelas[indice_atual]['periodos']:
                    tabelas[indice_atual]['periodos'] += [nome_periodo]
                tabelas[indice_atual]['categorias'] += [categoria]
                tabelas[indice_atual]['nomes_campos'] += sorted(
                    dict_categorias_campos[categoria], key=lambda k: ORDEM_CAMPOS[k])
                tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
            else:
                indice_atual += 1
                tabelas += [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [],
                             'len_categorias': [], 'valores_campos': []}]
                tabelas[indice_atual]['periodos'] += [nome_periodo]
                tabelas[indice_atual]['categorias'] += [categoria]
                tabelas[indice_atual]['nomes_campos'] += dict_categorias_campos[categoria]
                tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]

    get_tamanho_colunas_periodos(tabelas)

    return tabelas


def popula_campo_matriculados(tabela, dia, campo, indice_campo, indice_periodo, valores_dia, logs_alunos_matriculados):
    if campo == 'matriculados':
        if indice_campo > 1 and len(tabela['periodos']) > 1:
            indice_periodo += 1
        try:
            periodo = tabela['periodos'][indice_periodo]
            if '-' in periodo:
                periodo = periodo.split(' - ')[1]
            valores_dia += [logs_alunos_matriculados.get(
                periodo_escolar__nome=periodo,
                criado_em__day=dia,
            ).quantidade_alunos]
        except LogAlunosMatriculadosPeriodoEscola.DoesNotExist:
            valores_dia += ['0']


def popula_campo_aprovadas(solicitacao, dia, campo, categoria_corrente, valores_dia, logs_dietas):
    if campo == 'aprovadas':
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
                valores_dia += [quantidade or '0']
            else:
                valores_dia += [logs_dietas.get(
                    data__day=dia,
                    data__month=solicitacao.mes,
                    data__year=solicitacao.ano,
                    classificacao__nome=categoria_corrente.split(' - ')[1].title()
                ).quantidade]
        except LogQuantidadeDietasAutorizadas.DoesNotExist:
            valores_dia += ['0']


def popula_campos_preenchidos_pela_escola(solicitacao, tabela, campo, dia, indice_periodo, categoria_corrente,
                                          valores_dia):
    try:
        periodo = tabela['periodos'][indice_periodo]
        grupo = None
        if '-' in periodo:
            grupo = GrupoMedicao.objects.get(nome=periodo.split(' - ')[0])
            periodo = periodo.split(' - ')[1]
        valores_dia += [solicitacao.medicoes.get(
            periodo_escolar__nome=periodo,
            grupo=grupo
        ).valores_medicao.get(
            dia=f'{dia:02d}',
            categoria_medicao__nome=categoria_corrente,
            nome_campo=campo
        ).valor]
    except ValorMedicao.DoesNotExist:
        valores_dia += ['0']


def popula_campos(solicitacao, tabela, dia, indice_periodo, logs_alunos_matriculados, logs_dietas):
    valores_dia = [dia]
    indice_campo = 0
    indice_categoria = 0
    categoria_corrente = tabela['categorias'][indice_categoria]
    for campo in tabela['nomes_campos']:
        if indice_campo > tabela['len_categorias'][indice_categoria] - 1:
            indice_campo = 0
            indice_categoria += 1
            categoria_corrente = tabela['categorias'][indice_categoria]
        popula_campo_matriculados(tabela, dia, campo, indice_campo, indice_periodo, valores_dia,
                                  logs_alunos_matriculados)
        popula_campo_aprovadas(solicitacao, dia, campo, categoria_corrente, valores_dia, logs_dietas)
        # TODO: implementar total de refeições e total de sobremesas
        # TODO: quando categoria de Solicitações de Alimentação estiver implementada, tratar campo 'solicitado'
        if campo in ['solicitado', 'total_refeicoes_pagamento', 'total_sobremesas_pagamento']:
            valores_dia += ['0']
        elif campo not in ['matriculados', 'aprovadas']:
            popula_campos_preenchidos_pela_escola(solicitacao, tabela, campo, dia, indice_periodo, categoria_corrente,
                                                  valores_dia)
        indice_campo += 1
    tabela['valores_campos'] += [valores_dia]


def popula_tabelas(solicitacao, tabelas):
    dias_no_mes = range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1)
    logs_alunos_matriculados = LogAlunosMatriculadosPeriodoEscola.objects.filter(
        escola=solicitacao.escola, criado_em__month=solicitacao.mes,
        criado_em__year=solicitacao.ano, tipo_turma='REGULAR')
    logs_dietas = LogQuantidadeDietasAutorizadas.objects.filter(
        escola=solicitacao.escola, data__month=solicitacao.mes, data__year=solicitacao.ano)

    indice_periodo = 0
    quantidade_tabelas = range(0, len(tabelas))

    for indice_tabela in quantidade_tabelas:
        tabela = tabelas[indice_tabela]
        for dia in dias_no_mes:
            popula_campos(solicitacao, tabela, dia, indice_periodo, logs_alunos_matriculados, logs_dietas)

    return tabelas


def build_tabelas_relatorio_medicao(solicitacao):
    tabelas_com_headers = build_headers_tabelas(solicitacao)
    tabelas_populadas = popula_tabelas(solicitacao, tabelas_com_headers)

    return tabelas_populadas
