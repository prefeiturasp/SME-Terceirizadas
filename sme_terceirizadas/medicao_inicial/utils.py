from calendar import monthrange

from django.db.models import Sum

from sme_terceirizadas.dieta_especial.models import LogQuantidadeDietasAutorizadas
from sme_terceirizadas.escola.models import LogAlunosMatriculadosPeriodoEscola
from sme_terceirizadas.medicao_inicial.models import GrupoMedicao, ValorMedicao


def build_dict_relacao_categorias_e_campos(medicao):
    CATEGORIA = 0
    CAMPO = 1

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
    return dict_categorias_campos


def build_tabelas(solicitacao):
    MAX_COLUNAS = 15
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

    for tabela in tabelas:
        tabela['len_periodos'] = ([len(tabela['nomes_campos'])]
                                  if len(tabela['periodos']) == 1
                                  else tabela['len_categorias'])

    return tabelas


def build_tabelas_relatorio_medicao(solicitacao):
    tabelas = build_tabelas(solicitacao)

    dias_no_mes = range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1)
    indice_periodo = 0
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
                    if indice_campo > 1 and len(tabela['periodos']) > 1:
                        indice_periodo += 1
                    try:
                        periodo = tabela['periodos'][indice_periodo]
                        if '-' in periodo:
                            periodo = periodo.split(' - ')[1]
                        valores_dia += [logs_alunos_matriculados.get(
                            periodo_escolar__nome=periodo,
                            criado_em__day=dia
                        ).quantidade_alunos]
                    except LogAlunosMatriculadosPeriodoEscola.DoesNotExist:
                        valores_dia += ['0']
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
                        valores_dia += ['0']
                elif campo in ['solicitado', 'total_refeicoes_pagamento', 'total_sobremesas_pagamento']:
                    valores_dia += ['0']
                else:
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
                indice_campo += 1
            tabela['valores_campos'] += [valores_dia]
    return tabelas
