import datetime
from calendar import monthrange

from django.db.models import Sum

from sme_terceirizadas.dieta_especial.models import LogQuantidadeDietasAutorizadas
from sme_terceirizadas.escola.models import DiaCalendario, LogAlunosMatriculadosPeriodoEscola
from sme_terceirizadas.medicao_inicial.models import GrupoMedicao, ValorMedicao
from sme_terceirizadas.paineis_consolidados.models import SolicitacoesEscola


def get_lista_categorias_campos(medicao):
    lista_categorias_campos = sorted(list(
        medicao.valores_medicao.exclude(
            nome_campo__in=['observacoes', 'dietas_autorizadas', 'matriculados']
        ).values_list('categoria_medicao__nome', 'nome_campo').distinct()))
    if medicao.grupo and medicao.grupo.nome == 'Solicitações de Alimentação':
        lista_ = []
        if ('SOLICITAÇÕES DE ALIMENTAÇÃO', 'lanche_emergencial') in lista_categorias_campos:
            lista_ += [('LANCHE EMERGENCIAL', 'solicitado'), ('LANCHE EMERGENCIAL', 'consumido')]
        elif ('SOLICITAÇÕES DE ALIMENTAÇÃO', 'kit_lanche') in lista_categorias_campos:
            lista_ += [('KIT LANCHE', 'solicitado'), ('KIT LANCHE', 'consumido')]
        lista_categorias_campos = lista_
    return lista_categorias_campos


def build_dict_relacao_categorias_e_campos(medicao):
    CATEGORIA = 0
    CAMPO = 1

    lista_categorias_campos = get_lista_categorias_campos(medicao)
    dict_categorias_campos = {}
    for categoria_campo in lista_categorias_campos:
        if categoria_campo[CATEGORIA] not in dict_categorias_campos.keys():
            if 'DIETA' in categoria_campo[CATEGORIA]:
                dict_categorias_campos[categoria_campo[CATEGORIA]] = ['aprovadas']
            elif medicao.grupo and medicao.grupo.nome == 'Solicitações de Alimentação':
                dict_categorias_campos[categoria_campo[CATEGORIA]] = []
            elif medicao.grupo and medicao.grupo.nome in ['Programas e Projetos', 'ETEC']:
                dict_categorias_campos[categoria_campo[CATEGORIA]] = [
                    'total_refeicoes_pagamento', 'total_sobremesas_pagamento']
            else:
                dict_categorias_campos[categoria_campo[CATEGORIA]] = [
                    'matriculados', 'total_refeicoes_pagamento', 'total_sobremesas_pagamento']
            dict_categorias_campos[categoria_campo[CATEGORIA]] += [categoria_campo[CAMPO]]
        else:
            dict_categorias_campos[categoria_campo[CATEGORIA]] += [categoria_campo[CAMPO]]
    return dict_categorias_campos


def get_tamanho_colunas_periodos(tabelas):
    for tabela in tabelas:
        tabela['len_periodos'] = tabela['len_categorias']


def build_headers_tabelas(solicitacao):
    MAX_COLUNAS = 15
    ORDEM_CAMPOS = {
        'numero_de_alunos': -2,
        'matriculados': -1,
        'aprovadas': 0,
        'frequencia': 1,
        'solicitado': 2,
        'consumido': 3,
        'desjejum': 4,
        'lanche': 5,
        'lanche_4h': 6,
        'refeicao': 7,
        'repeticao_refeicao': 8,
        'lanche_emergencial': 9,
        'kit_lanche': 10,
        'total_refeicoes_pagamento': 11,
        'sobremesa': 12,
        'repeticao_sobremesa': 13,
        'total_sobremesas_pagamento': 14
    }

    tabelas = [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [], 'len_categorias': [],
                'valores_campos': [], 'ordem_periodos_grupos': [], 'dias_letivos': []}]

    indice_atual = 0
    ORDEM_PERIODOS_GRUPOS = {
        'MANHA': 1,
        'TARDE': 2,
        'INTEGRAL': 3,
        'NOITE': 4,
        'VESPERTINO': 5,
        'Programas e Projetos - MANHA': 6,
        'Programas e Projetos - TARDE': 7,
        'Solicitações de Alimentação': 8,
        'ETEC': 9
    }
    for medicao in sorted(solicitacao.medicoes.all(), key=lambda k: ORDEM_PERIODOS_GRUPOS[k.nome_periodo_grupo]):
        dict_categorias_campos = build_dict_relacao_categorias_e_campos(medicao)
        for categoria in dict_categorias_campos.keys():
            nome_periodo = (medicao.periodo_escolar.nome
                            if not medicao.grupo
                            else (f'{medicao.grupo.nome} - {medicao.periodo_escolar.nome}'
                                  if medicao.periodo_escolar else medicao.grupo.nome))
            if len(tabelas[indice_atual]['nomes_campos']) + len(dict_categorias_campos[categoria]) <= MAX_COLUNAS:
                if nome_periodo not in tabelas[indice_atual]['periodos']:
                    tabelas[indice_atual]['periodos'] += [nome_periodo]
                tabelas[indice_atual]['categorias'] += [categoria]
                tabelas[indice_atual]['nomes_campos'] += sorted(
                    dict_categorias_campos[categoria], key=lambda k: ORDEM_CAMPOS[k])
                tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
                tabelas[indice_atual]['ordem_periodos_grupos'] += [ORDEM_PERIODOS_GRUPOS[nome_periodo]]
            else:
                indice_atual += 1
                tabelas += [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [],
                             'len_categorias': [], 'valores_campos': [], 'ordem_periodos_grupos': [],
                             'dias_letivos': []}]
                tabelas[indice_atual]['periodos'] += [nome_periodo]
                tabelas[indice_atual]['categorias'] += [categoria]
                tabelas[indice_atual]['nomes_campos'] += sorted(
                    dict_categorias_campos[categoria], key=lambda k: ORDEM_CAMPOS[k])
                tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
                tabelas[indice_atual]['ordem_periodos_grupos'] += [ORDEM_PERIODOS_GRUPOS[nome_periodo]]

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
        medicoes = solicitacao.medicoes.all()
        if '-' in periodo:
            grupo = GrupoMedicao.objects.get(nome=periodo.split(' - ')[0])
            periodo = periodo.split(' - ')[1]
            medicao = medicoes.get(periodo_escolar__nome=periodo, grupo=grupo)
        elif periodo in ['ETEC', 'Solicitações de Alimentação']:
            medicao = medicoes.get(grupo__nome=periodo)
        else:
            medicao = medicoes.get(periodo_escolar__nome=periodo, grupo=None)
        valores_dia += [medicao.valores_medicao.get(
            dia=f'{dia:02d}',
            categoria_medicao__nome=categoria_corrente,
            nome_campo=campo
        ).valor]
    except ValorMedicao.DoesNotExist:
        valores_dia += ['0']


def popula_campo_consumido_solicitacoes_alimentacao(solicitacao, dia, campo, categoria_corrente, valores_dia):
    if campo == 'consumido':
        try:
            medicao = solicitacao.medicoes.get(grupo__nome__icontains='Solicitações')
            nome_campo = 'lanche_emergencial' if categoria_corrente == 'LANCHE EMERGENCIAL' else 'kit_lanche'
            valores_dia += [medicao.valores_medicao.get(
                dia=f'{dia:02d}',
                nome_campo=nome_campo
            ).valor]
        except Exception:
            valores_dia += ['0']


def popula_campo_total_refeicoes_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia):
    if campo == 'total_refeicoes_pagamento':
        try:
            campos = tabela['nomes_campos']
            valor_refeicao = valores_dia[campos.index('refeicao') + 1] if 'refeicao' in campos else 0
            valor_repeticao_refeicao = (
                valores_dia[campos.index('repeticao_refeicao') + 1] if 'repeticao_refeicao' in campos
                else 0)
            valor_matriculados = valores_dia[campos.index('matriculados') + 1] if 'matriculados' in campos else 0
            valor_numero_de_alunos = (
                valores_dia[campos.index('numero_de_alunos') + 1] if 'numero_de_alunos' in campos
                else 0)
            if solicitacao.escola.eh_emei:
                valores_dia += [valor_refeicao]
            else:
                total_refeicao = int(valor_refeicao) + int(valor_repeticao_refeicao)
                valor_comparativo = valor_matriculados if valor_matriculados > 0 else valor_numero_de_alunos
                if total_refeicao > int(valor_comparativo):
                    total_refeicao = max(int(valor_refeicao), int(valor_repeticao_refeicao))
                valores_dia += [total_refeicao]
        except Exception:
            valores_dia += ['0']


def popula_campo_total_sobremesas_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia):
    if campo == 'total_sobremesas_pagamento':
        try:
            campos = tabela['nomes_campos']
            valor_sobremesa = valores_dia[campos.index('sobremesa') + 1] if 'sobremesa' in campos else 0
            valor_repeticao_sobremesa = (
                valores_dia[campos.index('repeticao_sobremesa') + 1] if 'repeticao_sobremesa' in campos
                else 0)
            valor_matriculados = valores_dia[campos.index('matriculados') + 1] if 'matriculados' in campos else 0
            valor_numero_de_alunos = (
                valores_dia[campos.index('numero_de_alunos') + 1] if 'numero_de_alunos' in campos
                else 0)
            if solicitacao.escola.eh_emei:
                valores_dia += [valor_sobremesa]
            else:
                total_sobremesa = int(valor_sobremesa) + int(valor_repeticao_sobremesa)
                valor_comparativo = valor_matriculados if valor_matriculados > 0 else valor_numero_de_alunos
                if total_sobremesa > int(valor_comparativo):
                    total_sobremesa = max(int(valor_sobremesa), int(valor_repeticao_sobremesa))
                valores_dia += [total_sobremesa]
        except Exception:
            valores_dia += ['0']


def popula_campo_solicitado(
    solicitacao, tabela,
    campo, dia, categoria_corrente,
    valores_dia, alteracoes_lanche_emergencial
):
    if campo == 'solicitado':
        try:
            alteracao = [alt for alt in alteracoes_lanche_emergencial if alt['dia'] == f'{dia:02d}'][0]
            valores_dia += [alteracao['numero_alunos']]
        except Exception:
            valores_dia += ['0']


def popula_campo_total(tabela, campo, valores_dia):
    if campo in ['matriculados', 'numero_de_alunos', 'frequencia', 'aprovadas']:
        valores_dia += ['-']
    else:
        try:
            values = [valores[tabela['nomes_campos'].index(campo) + 1] for valores in tabela['valores_campos']]
            valores_dia += [sum(int(x) for x in values)]
        except Exception:
            valores_dia += ['0']


def get_eh_dia_letivo(dia, solicitacao):
    if not dia == 'Total':
        try:
            eh_dia_letivo = DiaCalendario.objects.get(
                escola=solicitacao.escola,
                data__day=dia,
                data__month=solicitacao.mes,
                data__year=solicitacao.ano
            ).dia_letivo
            return eh_dia_letivo
        except Exception:
            return False


def popula_campos(
    solicitacao,
    tabela, dia,
    indice_periodo,
    logs_alunos_matriculados,
    logs_dietas, alteracoes_lanche_emergencial
):
    valores_dia = [dia]
    eh_dia_letivo = get_eh_dia_letivo(dia, solicitacao)
    indice_campo = 0
    indice_categoria = 0
    categoria_corrente = tabela['categorias'][indice_categoria]
    for campo in tabela['nomes_campos']:
        if indice_campo > tabela['len_categorias'][indice_categoria] - 1:
            indice_campo = 0
            indice_categoria += 1
            categoria_corrente = tabela['categorias'][indice_categoria]
        if dia == 'Total':
            popula_campo_total(tabela, campo, valores_dia)
        else:
            popula_campo_matriculados(
                tabela, dia, campo, indice_campo,
                indice_periodo, valores_dia,
                logs_alunos_matriculados)
            popula_campo_aprovadas(solicitacao, dia, campo, categoria_corrente, valores_dia, logs_dietas)
            popula_campo_consumido_solicitacoes_alimentacao(solicitacao, dia, campo, categoria_corrente, valores_dia)
            popula_campo_total_refeicoes_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia)
            popula_campo_total_sobremesas_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia)
            popula_campo_solicitado(
                solicitacao, tabela, campo, dia,
                categoria_corrente, valores_dia,
                alteracoes_lanche_emergencial)
            if campo not in [
                'matriculados',
                'aprovadas',
                'total_refeicoes_pagamento',
                'total_sobremesas_pagamento',
                'solicitado',
                'consumido'
            ]:
                popula_campos_preenchidos_pela_escola(
                    solicitacao, tabela, campo, dia,
                    indice_periodo, categoria_corrente,
                    valores_dia)
        indice_campo += 1
    tabela['valores_campos'] += [valores_dia]
    tabela['dias_letivos'] += [eh_dia_letivo if not dia == 'Total' else False]


def popula_tabelas(solicitacao, tabelas):
    dias_no_mes = range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1)
    logs_alunos_matriculados = LogAlunosMatriculadosPeriodoEscola.objects.filter(
        escola=solicitacao.escola, criado_em__month=solicitacao.mes,
        criado_em__year=solicitacao.ano, tipo_turma='REGULAR')
    logs_dietas = LogQuantidadeDietasAutorizadas.objects.filter(
        escola=solicitacao.escola, data__month=solicitacao.mes, data__year=solicitacao.ano)

    escola_uuid = solicitacao.escola.uuid
    mes = solicitacao.mes
    ano = solicitacao.ano
    query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
    query_set = query_set.filter(data_evento__month=mes, data_evento__year=ano)
    query_set = query_set.filter(data_evento__lt=datetime.date.today())
    query_set = query_set.filter(motivo__icontains='Emergencial')
    aux = []
    sem_uuid_repetido = []
    for resultado in query_set:
        if resultado.uuid not in aux:
            aux.append(resultado.uuid)
            sem_uuid_repetido.append(resultado)
    query_set = sem_uuid_repetido
    alteracoes_lanche_emergencial = []
    for alteracao_alimentacao in query_set:
        alteracao = alteracao_alimentacao.get_raw_model.objects.get(uuid=alteracao_alimentacao.uuid)
        alteracoes_lanche_emergencial.append({
            'dia': f'{alteracao.data.day:02d}',
            'numero_alunos': sum([sub.qtd_alunos for sub in alteracao.substituicoes_periodo_escolar.all()]),
        })

    indice_periodo = 0
    quantidade_tabelas = range(0, len(tabelas))

    for indice_tabela in quantidade_tabelas:
        tabela = tabelas[indice_tabela]
        for dia in list(dias_no_mes) + ['Total']:
            popula_campos(
                solicitacao, tabela, dia, indice_periodo,
                logs_alunos_matriculados, logs_dietas,
                alteracoes_lanche_emergencial)

    return tabelas


def build_tabelas_relatorio_medicao(solicitacao):
    tabelas_com_headers = build_headers_tabelas(solicitacao)
    tabelas_populadas = popula_tabelas(solicitacao, tabelas_com_headers)

    return tabelas_populadas


def tratar_valores(escola, valores):
    if escola.eh_emei:
        campos_repeticao = ['repeticao_refeicao', 'repeticao_sobremesa']
        valores = [valor for valor in valores if valor['nome_campo'] not in campos_repeticao]
    else:
        repeticao_refeicao = [valor for valor in valores if valor['nome_campo'] == 'repeticao_refeicao']
        repeticao_sobremesa = [valor for valor in valores if valor['nome_campo'] == 'repeticao_sobremesa']
        if repeticao_refeicao:
            valor_repeticao_refeicao = repeticao_refeicao[0]['valor']
            valor_refeicao = [valor for valor in valores if valor['nome_campo'] == 'refeicao'][0]['valor']
            campos_refeicao = ['refeicao', 'repeticao_refeicao']
            valores = [valor for valor in valores if valor['nome_campo'] not in campos_refeicao]
            valores.append({
                'nome_campo': 'refeicao',
                'valor': valor_repeticao_refeicao + valor_refeicao,
            })
        if repeticao_sobremesa:
            valor_repeticao_sobremesa = repeticao_sobremesa[0]['valor']
            valor_sobremesa = [valor for valor in valores if valor['nome_campo'] == 'sobremesa'][0]['valor']
            campos_sobremesa = ['sobremesa', 'repeticao_sobremesa']
            valores = [valor for valor in valores if valor['nome_campo'] not in campos_sobremesa]
            valores.append({
                'nome_campo': 'sobremesa',
                'valor': valor_repeticao_sobremesa + valor_sobremesa,
            })
    return valores
