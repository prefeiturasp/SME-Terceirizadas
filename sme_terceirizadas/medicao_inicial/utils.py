import datetime
import json
from calendar import monthrange

from django.db.models import Sum

from sme_terceirizadas.dados_comuns.constants import ORDEM_PERIODOS_GRUPOS
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile
from sme_terceirizadas.dieta_especial.models import LogQuantidadeDietasAutorizadas
from sme_terceirizadas.escola.models import DiaCalendario, LogAlunosMatriculadosPeriodoEscola
from sme_terceirizadas.medicao_inicial.models import ValorMedicao
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
        if ('SOLICITAÇÕES DE ALIMENTAÇÃO', 'kit_lanche') in lista_categorias_campos:
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


def get_tamanho_colunas_periodos(tabelas, ORDEM_PERIODOS_GRUPOS):
    for tabela in tabelas:
        for periodo in tabela['periodos']:
            tabela['len_periodos'] += [sum(x['numero_campos'] for x in tabela['categorias_dos_periodos'][periodo])]
            tabela['ordem_periodos_grupos'] += [ORDEM_PERIODOS_GRUPOS[periodo]]


def get_categorias_dos_periodos(nome_periodo, tabelas, indice_atual, categoria, dict_categorias_campos):
    if nome_periodo in tabelas[indice_atual]['categorias_dos_periodos'].keys():
        tabelas[indice_atual]['categorias_dos_periodos'][nome_periodo].append({
            'categoria': categoria,
            'numero_campos': len(dict_categorias_campos[categoria])
        })
    else:
        tabelas[indice_atual]['categorias_dos_periodos'][nome_periodo] = [{
            'categoria': categoria,
            'numero_campos': len(dict_categorias_campos[categoria])
        }]


def build_headers_tabelas(solicitacao):
    MAX_COLUNAS = 15
    ORDEM_CAMPOS = {
        'numero_de_alunos': 1,
        'matriculados': 2,
        'aprovadas': 3,
        'frequencia': 4,
        'solicitado': 5,
        'consumido': 6,
        'desjejum': 7,
        'lanche': 8,
        'lanche_4h': 9,
        'refeicao': 10,
        'repeticao_refeicao': 11,
        'kit_lanche': 12,
        'total_refeicoes_pagamento': 13,
        'sobremesa': 14,
        'repeticao_sobremesa': 15,
        'total_sobremesas_pagamento': 16,
        'lanche_emergencial': 17
    }

    tabelas = [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [], 'len_categorias': [],
                'valores_campos': [], 'ordem_periodos_grupos': [], 'dias_letivos': [], 'categorias_dos_periodos': {}}]

    indice_atual = 0
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
                get_categorias_dos_periodos(nome_periodo, tabelas, indice_atual, categoria, dict_categorias_campos)
            else:
                indice_atual += 1
                tabelas += [{'periodos': [], 'categorias': [], 'nomes_campos': [], 'len_periodos': [],
                             'len_categorias': [], 'valores_campos': [], 'ordem_periodos_grupos': [],
                             'dias_letivos': [], 'categorias_dos_periodos': {}}]
                tabelas[indice_atual]['periodos'] += [nome_periodo]
                tabelas[indice_atual]['categorias'] += [categoria]
                tabelas[indice_atual]['nomes_campos'] += sorted(
                    dict_categorias_campos[categoria], key=lambda k: ORDEM_CAMPOS[k])
                tabelas[indice_atual]['len_categorias'] += [len(dict_categorias_campos[categoria])]
                get_categorias_dos_periodos(nome_periodo, tabelas, indice_atual, categoria, dict_categorias_campos)

    get_tamanho_colunas_periodos(tabelas, ORDEM_PERIODOS_GRUPOS)

    return tabelas


def popula_campo_matriculados(
    tabela, dia, campo, indice_campo,
    indice_periodo, valores_dia,
    logs_alunos_matriculados,
    categoria_corrente
):
    if campo == 'matriculados':
        try:
            periodo = tabela['periodos'][indice_periodo]
            log = logs_alunos_matriculados.filter(periodo_escolar__nome=periodo, criado_em__day=dia).first()
            if log:
                valores_dia += [log.quantidade_alunos]
            else:
                valores_dia += ['0']
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
                log_selec = logs_dietas.filter(
                    data__day=dia,
                    data__month=solicitacao.mes,
                    data__year=solicitacao.ano,
                    classificacao__nome=categoria_corrente.split(' - ')[1].title()
                ).first()
                if not log_selec:
                    valores_dia += ['0']
                else:
                    valores_dia += [log_selec.quantidade]
        except LogQuantidadeDietasAutorizadas.DoesNotExist:
            valores_dia += ['0']


def popula_campos_preenchidos_pela_escola(solicitacao, tabela, campo, dia, indice_periodo, categoria_corrente,
                                          valores_dia):
    try:
        periodo = tabela['periodos'][indice_periodo]
        medicoes = solicitacao.medicoes.all()
        if periodo in ['ETEC', 'Solicitações de Alimentação', 'Programas e Projetos']:
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


def get_index_refeicao(indexes_refeicao, indice_periodo):
    if len(indexes_refeicao) > 1:
        index_refeicao = indexes_refeicao[indice_periodo]
    else:
        index_refeicao = indexes_refeicao[0]
    return index_refeicao


def popula_campo_total_refeicoes_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia, indice_periodo):
    if campo == 'total_refeicoes_pagamento':
        try:
            campos = tabela['nomes_campos']
            indexes_refeicao = [i for i, campo in enumerate(campos) if campo == 'refeicao']
            index_refeicao = get_index_refeicao(indexes_refeicao, indice_periodo)
            valor_refeicao = valores_dia[index_refeicao + 1] if 'refeicao' in campos else 0
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
    valores_dia, alteracoes_lanche_emergencial,
    kits_lanches
):
    if campo == 'solicitado':
        try:
            if categoria_corrente == 'LANCHE EMERGENCIAL':
                alteracao = [alt for alt in alteracoes_lanche_emergencial if alt['dia'] == f'{dia:02d}'][0]
                valores_dia += [alteracao['numero_alunos']]
            else:
                kit = [kit for kit in kits_lanches if kit['dia'] == f'{dia:02d}'][0]
                valores_dia += [kit['numero_alunos']]
        except Exception:
            valores_dia += ['0']


def popula_campo_total(tabela, campo, valores_dia, indice_categoria, indice_campo, categoria_corrente):
    if campo in ['matriculados', 'numero_de_alunos', 'frequencia', 'aprovadas']:
        valores_dia += ['-']
    else:
        try:
            if indice_categoria == 0:
                values = [valores[tabela['nomes_campos'].index(campo) + 1] for valores in tabela['valores_campos']]
            else:
                i = 1
                indice_valor_campo = 0
                while i <= indice_categoria:
                    indice_valor_campo += tabela['len_categorias'][indice_categoria - i]
                    i += 1
                indice_valor_campo += indice_campo
                values = [valores[indice_valor_campo + 1] for valores in tabela['valores_campos']]
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
    logs_dietas, alteracoes_lanche_emergencial,
    kits_lanches
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
            periodo_corrente = tabela['periodos'][indice_periodo]
            if (
                indice_categoria > len(tabela['categorias_dos_periodos'][periodo_corrente]) - 1
                and indice_periodo + 1 < len(tabela['periodos'])
            ):
                indice_periodo += 1
        if dia == 'Total':
            popula_campo_total(tabela, campo, valores_dia, indice_categoria, indice_campo, categoria_corrente)
        else:
            popula_campo_matriculados(
                tabela, dia, campo, indice_campo,
                indice_periodo, valores_dia,
                logs_alunos_matriculados,
                categoria_corrente)
            popula_campo_aprovadas(solicitacao, dia, campo, categoria_corrente, valores_dia, logs_dietas)
            popula_campo_consumido_solicitacoes_alimentacao(solicitacao, dia, campo, categoria_corrente, valores_dia)
            popula_campo_total_refeicoes_pagamento(
                solicitacao, tabela,
                campo, categoria_corrente,
                valores_dia, indice_periodo)
            popula_campo_total_sobremesas_pagamento(solicitacao, tabela, campo, categoria_corrente, valores_dia)
            popula_campo_solicitado(
                solicitacao, tabela, campo, dia,
                categoria_corrente, valores_dia,
                alteracoes_lanche_emergencial,
                kits_lanches)
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


def get_alteracoes_lanche_emergencial(solicitacao):
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
    return alteracoes_lanche_emergencial


def get_kit_lanche(solicitacao):
    escola_uuid = solicitacao.escola.uuid
    mes = solicitacao.mes
    ano = solicitacao.ano
    query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
    query_set = query_set.filter(data_evento__month=mes, data_evento__year=ano)
    query_set = query_set.filter(data_evento__lt=datetime.date.today())
    query_set = query_set.filter(desc_doc__icontains='Kit Lanche')
    aux = []
    sem_uuid_repetido = []
    for resultado in query_set:
        if resultado.uuid not in aux:
            aux.append(resultado.uuid)
            sem_uuid_repetido.append(resultado)
    query_set = sem_uuid_repetido
    kits_lanches = []
    for kit_lanche in query_set:
        kit_lanche = kit_lanche.get_raw_model.objects.get(uuid=kit_lanche.uuid)
        if kit_lanche:
            kits_lanches.append({
                'dia': f'{kit_lanche.solicitacao_kit_lanche.data.day:02d}',
                'numero_alunos': kit_lanche.quantidade_alimentacoes
            })

    return kits_lanches


def popula_tabelas(solicitacao, tabelas):
    dias_no_mes = range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1)
    logs_alunos_matriculados = LogAlunosMatriculadosPeriodoEscola.objects.filter(
        escola=solicitacao.escola, criado_em__month=solicitacao.mes,
        criado_em__year=solicitacao.ano, tipo_turma='REGULAR')
    logs_dietas = LogQuantidadeDietasAutorizadas.objects.filter(
        escola=solicitacao.escola, data__month=solicitacao.mes, data__year=solicitacao.ano)

    alteracoes_lanche_emergencial = get_alteracoes_lanche_emergencial(solicitacao)
    kits_lanches = get_kit_lanche(solicitacao)

    indice_periodo = 0
    quantidade_tabelas = range(0, len(tabelas))

    for indice_tabela in quantidade_tabelas:
        tabela = tabelas[indice_tabela]
        for dia in list(dias_no_mes) + ['Total']:
            popula_campos(
                solicitacao, tabela, dia, indice_periodo,
                logs_alunos_matriculados, logs_dietas,
                alteracoes_lanche_emergencial,
                kits_lanches)

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
            obj_refeicao = [valor for valor in valores if valor['nome_campo'] == 'refeicao']
            valor_refeicao = obj_refeicao[0]['valor'] if obj_refeicao else 0
            campos_refeicao = ['refeicao', 'repeticao_refeicao']
            valores = [valor for valor in valores if valor['nome_campo'] not in campos_refeicao]
            valores.append({
                'nome_campo': 'refeicao',
                'valor': valor_repeticao_refeicao + valor_refeicao,
            })
        if repeticao_sobremesa:
            valor_repeticao_sobremesa = repeticao_sobremesa[0]['valor']
            obj_sobremesa = [valor for valor in valores if valor['nome_campo'] == 'sobremesa']
            valor_sobremesa = obj_sobremesa[0]['valor'] if obj_sobremesa else 0
            campos_sobremesa = ['sobremesa', 'repeticao_sobremesa']
            valores = [valor for valor in valores if valor['nome_campo'] not in campos_sobremesa]
            valores.append({
                'nome_campo': 'sobremesa',
                'valor': valor_repeticao_sobremesa + valor_sobremesa,
            })
    return valores


def get_nome_campo(campo):
    campos = {
        'desjejum': 'Desjejum',
        'lanche': 'Lanche',
        'lanche_4h': 'Lanche 4h',
        'refeicao': 'Refeição',
        'repeticao_refeicao': 'Repetição de Refeição',
        'lanche_emergencial': 'Lanche Emergencial',
        'kit_lanche': 'Kit Lanche',
        'sobremesa': 'Sobremesa',
        'repeticao_sobremesa': 'Repetição de Sobremesa',
    }
    return campos.get(campo, campo)


def somar_valores_de_repeticao(values, medicao, campo, solicitacao):
    if not solicitacao.escola.eh_emei:
        if campo == 'refeicao':
            values_repeticao_refeicao = medicao.valores_medicao.filter(
                categoria_medicao__nome='ALIMENTAÇÃO', nome_campo='repeticao_refeicao'
            )
            values = values | values_repeticao_refeicao
        if campo == 'sobremesa':
            values_repeticao_sobremesa = medicao.valores_medicao.filter(
                categoria_medicao__nome='ALIMENTAÇÃO', nome_campo='repeticao_sobremesa'
            )
            values = values | values_repeticao_sobremesa
    return values


def get_somatorio_manha(campo, solicitacao):
    try:
        medicao = solicitacao.medicoes.get(periodo_escolar__nome='MANHA', grupo=None)
        values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
        values = somar_valores_de_repeticao(values, medicao, campo, solicitacao)
        somatorio_manha = sum([int(v.valor) for v in values])
        if somatorio_manha == 0:
            somatorio_manha = ' - '
    except Exception:
        somatorio_manha = ' - '
    return somatorio_manha


def get_somatorio_tarde(campo, solicitacao):
    try:
        medicao = solicitacao.medicoes.get(periodo_escolar__nome='TARDE', grupo=None)
        values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
        values = somar_valores_de_repeticao(values, medicao, campo, solicitacao)
        somatorio_tarde = sum([int(v.valor) for v in values])
        if somatorio_tarde == 0:
            somatorio_tarde = ' - '
    except Exception:
        somatorio_tarde = ' - '
    return somatorio_tarde


def get_somatorio_integral(campo, solicitacao):
    try:
        medicao = solicitacao.medicoes.get(periodo_escolar__nome='INTEGRAL', grupo=None)
        values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
        values = somar_valores_de_repeticao(values, medicao, campo, solicitacao)
        somatorio_integral = sum([int(v.valor) for v in values])
        if somatorio_integral == 0:
            somatorio_integral = ' - '
    except Exception:
        somatorio_integral = ' - '
    return somatorio_integral


def get_somatorio_programas_e_projetos(campo, solicitacao):
    try:
        medicoes = solicitacao.medicoes.filter(grupo__nome='Programas e Projetos')
        values = []
        for medicao in medicoes:
            qs_values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
            qs_values = somar_valores_de_repeticao(qs_values, medicao, campo, solicitacao)
            [values.append(v.valor) for v in qs_values]
        somatorio_programas_e_projetos = sum([int(v) for v in values])
        if somatorio_programas_e_projetos == 0:
            somatorio_programas_e_projetos = ' - '
    except Exception:
        somatorio_programas_e_projetos = ' - '
    return somatorio_programas_e_projetos


def get_somatorio_solicitacoes_de_alimentacao(campo, solicitacao):
    try:
        medicao = solicitacao.medicoes.get(grupo__nome='Solicitações de Alimentação')
        values = medicao.valores_medicao.filter(nome_campo=campo)
        somatorio_solicitacoes_de_alimentacao = sum([int(v.valor) for v in values])
        if somatorio_solicitacoes_de_alimentacao == 0:
            somatorio_solicitacoes_de_alimentacao = ' - '
    except Exception:
        somatorio_solicitacoes_de_alimentacao = ' - '
    return somatorio_solicitacoes_de_alimentacao


def get_somatorio_total_tabela(valores_somatorios_tabela):
    valores_somatorio = []
    [valores_somatorio.append(v) for v in valores_somatorios_tabela if v != ' - ']
    try:
        somatorio_total_tabela = sum([int(v) for v in valores_somatorio])
        if somatorio_total_tabela == 0:
            somatorio_total_tabela = ' - '
    except Exception:
        somatorio_total_tabela = ' - '
    return somatorio_total_tabela


def get_somatorio_noite_eja(campo, solicitacao):
    # ajustar para filtrar periodo/grupo EJA
    try:
        medicao = solicitacao.medicoes.get(periodo_escolar__nome='NOITE', grupo=None)
        values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
        values = somar_valores_de_repeticao(values, medicao, campo, solicitacao)
        somatorio_noite = sum([int(v.valor) for v in values])
        if somatorio_noite == 0:
            somatorio_noite = ' - '
    except Exception:
        somatorio_noite = ' - '
    return somatorio_noite


def get_somatorio_etec(campo, solicitacao):
    try:
        medicao = solicitacao.medicoes.get(grupo__nome='ETEC')
        values = medicao.valores_medicao.filter(categoria_medicao__nome='ALIMENTAÇÃO', nome_campo=campo)
        values = somar_valores_de_repeticao(values, medicao, campo, solicitacao)
        somatorio_etec = sum([int(v.valor) for v in values])
        if somatorio_etec == 0:
            somatorio_etec = ' - '
    except Exception:
        somatorio_etec = ' - '
    return somatorio_etec


def build_tabela_somatorio_body(solicitacao):
    ORDEM_CAMPOS = {
        'numero_de_alunos': 1,
        'matriculados': 2,
        'aprovadas': 3,
        'frequencia': 4,
        'solicitado': 5,
        'consumido': 6,
        'desjejum': 7,
        'lanche': 8,
        'lanche_4h': 9,
        'refeicao': 10,
        'repeticao_refeicao': 11,
        'kit_lanche': 12,
        'total_refeicoes_pagamento': 13,
        'sobremesa': 14,
        'repeticao_sobremesa': 15,
        'total_sobremesas_pagamento': 16,
        'lanche_emergencial': 17
    }
    campos_tipos_alimentacao = []
    for medicao in sorted(solicitacao.medicoes.all(), key=lambda k: ORDEM_PERIODOS_GRUPOS[k.nome_periodo_grupo]):
        campos = medicao.valores_medicao.exclude(
            nome_campo__in=[
                'observacoes',
                'dietas_autorizadas',
                'frequencia',
                'matriculados',
                'numero_de_alunos',
                'repeticao_refeicao',
                'repeticao_sobremesa'
            ]
        ).values_list('nome_campo', flat=True).distinct()
        [campos_tipos_alimentacao.append(campo) for campo in campos if campo not in campos_tipos_alimentacao]
    campos_tipos_alimentacao = sorted(campos_tipos_alimentacao, key=lambda k: ORDEM_CAMPOS[k])
    # head_tabela_somatorio_fixo em relatorio_solicitacao_medicao_por_escola.html: E800 noqa
    # 10 colunas conforme abaixo
    # [ E800 noqa
    #    'TIPOS DE ALIMENTAÇÃO', 'MANHÃ', 'TARDE', 'INTEGRAL', 'PROGRAMAS E PROJETOS', 'SOLICITAÇÕES DE ALIMENTAÇÃO', 'TOTAL', # noqa E501
    #    'NOITE/EJA', 'ETEC', 'TOTAL'
    # ] E800 noqa
    body_tabela_somatorio = []
    for tipo_alimentacao in campos_tipos_alimentacao:
        somatorio_manha = get_somatorio_manha(tipo_alimentacao, solicitacao)
        somatorio_tarde = get_somatorio_tarde(tipo_alimentacao, solicitacao)
        somatorio_integral = get_somatorio_integral(tipo_alimentacao, solicitacao)
        somatorio_programas_e_projetos = get_somatorio_programas_e_projetos(tipo_alimentacao, solicitacao)
        somatorio_solicitacoes_de_alimentacao = get_somatorio_solicitacoes_de_alimentacao(tipo_alimentacao, solicitacao)
        valores_somatorios_primeira_tabela = [
            somatorio_manha,
            somatorio_tarde,
            somatorio_integral,
            somatorio_programas_e_projetos,
            somatorio_solicitacoes_de_alimentacao
        ]
        somatorio_total_primeira_tabela = get_somatorio_total_tabela(valores_somatorios_primeira_tabela)
        somatorio_noite_eja = get_somatorio_noite_eja(tipo_alimentacao, solicitacao)
        somatorio_etec = get_somatorio_etec(tipo_alimentacao, solicitacao)
        valores_somatorios_segunda_tabela = [
            somatorio_noite_eja,
            somatorio_etec
        ]
        somatorio_total_segunda_tabela = get_somatorio_total_tabela(valores_somatorios_segunda_tabela)
        body_tabela_somatorio.append(
            [
                get_nome_campo(tipo_alimentacao),
                somatorio_manha, somatorio_tarde,
                somatorio_integral, somatorio_programas_e_projetos,
                somatorio_solicitacoes_de_alimentacao,
                somatorio_total_primeira_tabela,
                somatorio_noite_eja, somatorio_etec,
                somatorio_total_segunda_tabela
            ]
        )
    return body_tabela_somatorio


def atualizar_anexos_ocorrencia(
    anexos,
    solicitacao_medicao_inicial
):
    for anexo in anexos:
        if '.pdf' in anexo['nome']:
            arquivo = convert_base64_to_contentfile(anexo['base64'])
            solicitacao_medicao_inicial.ocorrencia.ultimo_arquivo = arquivo
            solicitacao_medicao_inicial.ocorrencia.nome_ultimo_arquivo = anexo.get('nome')
            solicitacao_medicao_inicial.ocorrencia.save()


def atualizar_status_ocorrencia(
    status_ocorrencia,
    status_correcao_solicitada_codae,
    solicitacao_medicao_inicial,
    request,
    justificativa
):
    if status_ocorrencia == status_correcao_solicitada_codae:
        solicitacao_medicao_inicial.ocorrencia.ue_corrige_ocorrencia_para_codae(
            user=request.user, justificativa=justificativa)
    else:
        solicitacao_medicao_inicial.ocorrencia.ue_corrige(user=request.user, justificativa=justificativa)


def dict_informacoes_iniciais(user, acao):
    return {
        'usuario': {'uuid': str(user.uuid), 'nome': user.nome,
                    'username': user.username, 'email': user.email},
        'criado_em': datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S'),
        'acao': acao,
        'alteracoes': []
    }


def criar_log_solicitar_correcao_periodos(user, solicitacao, acao):
    log = dict_informacoes_iniciais(user, acao)

    for medicao in solicitacao.medicoes.filter(status='MEDICAO_CORRECAO_SOLICITADA'):
        if medicao.periodo_escolar:
            periodo_nome = medicao.periodo_escolar.nome
        else:
            periodo_nome = medicao.grupo.nome

        alteracoes_dict = {
            'periodo_escolar': periodo_nome,
            'justificativa': medicao.logs.last().justificativa,
            'tabelas_lancamentos': []
        }

        valores_medicao = medicao.valores_medicao.filter(habilitado_correcao=True).order_by('semana')
        tabelas_lancamentos = valores_medicao.order_by(
            'categoria_medicao__nome'
        ).values_list('categoria_medicao__nome',
                      flat=True).distinct()

        for tabela in tabelas_lancamentos:
            valores_da_tabela = valores_medicao.filter(categoria_medicao__nome=tabela)
            semanas = valores_da_tabela.values_list('semana', flat=True).distinct()
            tabela_dict = {
                'categoria_medicao': tabela,
                'semanas': []
            }

            for semana in semanas:
                dias = valores_da_tabela.filter(semana=semana)
                dias = list(
                    dias.order_by('dia').values_list('dia', flat=True).distinct()
                )
                semana_dict = {'semana': semana, 'dias': dias}
                tabela_dict['semanas'].append(semana_dict)
            alteracoes_dict['tabelas_lancamentos'].append(tabela_dict)
        log['alteracoes'].append(alteracoes_dict)
    return log


def log_anterior_para_busca(acao):
    if acao == 'MEDICAO_APROVADA_PELA_DRE':
        return 'MEDICAO_CORRECAO_SOLICITADA'
    return 'MEDICAO_CORRECAO_SOLICITADA_CODAE'


def criar_log_aprovar_periodos_corrigidos(user, solicitacao, acao):
    log = dict_informacoes_iniciais(user, acao)
    historico = json.loads(solicitacao.historico)
    lista_logs = list(filter(lambda log: log['acao'] == log_anterior_para_busca(acao), historico))
    for log_do_historico in lista_logs:
        for alteracao in log_do_historico['alteracoes']:
            log['alteracoes'].append({'periodo_escolar': alteracao['periodo_escolar']})
    return log


def encontrar_ou_criar_log_inicial(user, acao, historico):
    lista_logs = list(filter(lambda log: log['acao'] == acao and log == historico[-1], historico))
    if not lista_logs:
        return dict_informacoes_iniciais(user, acao)
    else:
        return lista_logs[0]


def gerar_dicionario_e_buscar_valores_medicao(data, medicao):
    dicionario_alteracoes = {}
    for valor_atualizado in data:
        if not valor_atualizado:
            continue
        valor_medicao = ValorMedicao.objects.filter(
            medicao=medicao,
            dia=valor_atualizado.get('dia', ''),
            nome_campo=valor_atualizado.get('nome_campo', ''),
            categoria_medicao=valor_atualizado.get('categoria_medicao', '')
        )
        if not valor_medicao or str(valor_medicao.first().valor) == str(valor_atualizado.get('valor', '')):
            continue
        else:
            dicionario_alteracoes[f'{str(valor_medicao.first().uuid)}'] = valor_atualizado.get('valor', '')
    valores_medicao = ValorMedicao.objects.filter(uuid__in=list(dicionario_alteracoes.keys()))
    return dicionario_alteracoes, valores_medicao


def criar_log_escola_corrigiu(medicao, valores_medicao, dicionario_alteracoes, log_inicial, historico, solicitacao):
    if medicao.periodo_escolar:
        periodo_nome = medicao.periodo_escolar.nome
    else:
        periodo_nome = medicao.grupo.nome
    alteracoes_dict = {
        'periodo_escolar': periodo_nome,
        'tabelas_lancamentos': []
    }
    tabelas_lancamentos = valores_medicao.values_list('categoria_medicao__nome', flat=True).distinct()

    for tabela in tabelas_lancamentos:
        valores_da_tabela = valores_medicao.filter(categoria_medicao__nome=tabela)
        semanas = valores_da_tabela.values_list('semana', flat=True).distinct()
        tabela_dict = {
            'categoria_medicao': tabela,
            'semanas': []
        }

        for semana in semanas:
            dias = list(valores_da_tabela.filter(semana=semana).values_list('dia', flat=True).distinct())
            semana_dict = {'semana': semana, 'dias': []}

            for dia in dias:
                dia_dict = {'dia': dia, 'campos': []}
                nomes_dos_campos = valores_da_tabela.filter(dia=dia).values_list('nome_campo', flat=True).distinct()

                for campo in nomes_dos_campos:
                    vm = valores_da_tabela.get(semana=semana,
                                               dia=dia, nome_campo=campo,
                                               categoria_medicao__nome=tabela,
                                               medicao=medicao)

                    dia_dict['campos'].append({'campo_nome': campo,
                                               'de': vm.valor,
                                               'para': dicionario_alteracoes[str(vm.uuid)]})

                semana_dict['dias'].append(dia_dict)
            tabela_dict['semanas'].append(semana_dict)
        alteracoes_dict['tabelas_lancamentos'].append(tabela_dict)
    log_inicial['alteracoes'].append(alteracoes_dict)
    historico.append(log_inicial)
    solicitacao.historico = json.dumps(historico)
    solicitacao.save()


def get_alteracoes_log(lista_alteracoes, log_inicial, periodo_nome):
    if not lista_alteracoes:
        log_inicial['alteracoes'].append({'periodo_escolar': periodo_nome,
                                          'tabelas_lancamentos': []})
        cp_alteracao_dict = log_inicial['alteracoes'][-1]
    else:
        cp_alteracao_dict = lista_alteracoes[0]
    alteracao_idx = log_inicial['alteracoes'].index(cp_alteracao_dict)
    return log_inicial, cp_alteracao_dict, alteracao_idx


def atualiza_ou_cria_tabela_lancamentos_log(valor_medicao, cp_alteracao_dict, log_inicial, alteracao_idx):
    categoria_medicao = valor_medicao.categoria_medicao.nome
    lista = cp_alteracao_dict['tabelas_lancamentos']
    lista_categorias = list(filter(lambda tabela: tabela['categoria_medicao'] == categoria_medicao, lista))
    if not lista_categorias:
        log_inicial['alteracoes'][alteracao_idx]['tabelas_lancamentos'].append(
            {'categoria_medicao': categoria_medicao, 'semanas': []}
        )
        cp_categorias_dict = log_inicial['alteracoes'][alteracao_idx]['tabelas_lancamentos'][-1]
    else:
        cp_categorias_dict = lista_categorias[0]
    categoria_idx = cp_alteracao_dict['tabelas_lancamentos'].index(cp_categorias_dict)
    return log_inicial, cp_categorias_dict, categoria_idx


def atualiza_ou_cria_semanas_log(lista_semanas, log_inicial, alteracao_idx, categoria_idx,
                                 valor_medicao, cp_categorias_dict):
    if not lista_semanas:
        log_inicial['alteracoes'][alteracao_idx]['tabelas_lancamentos'][categoria_idx]['semanas'].append(
            {'semana': valor_medicao.semana, 'dias': []}
        )
        cp_semana_dict = log_inicial['alteracoes'][alteracao_idx]
        cp_semana_dict = cp_semana_dict['tabelas_lancamentos'][categoria_idx]['semanas'][-1]
    else:
        cp_semana_dict = lista_semanas[0]
    semana_idx = cp_categorias_dict['semanas'].index(cp_semana_dict)
    return log_inicial, semana_idx, cp_semana_dict


def atualiza_ou_cria_dias_log(lista_dias, log_inicial, alteracao_idx, categoria_idx,
                              semana_idx, valor_medicao, cp_semana_dict):
    if not lista_dias:
        (log_inicial['alteracoes'][alteracao_idx]
                    ['tabelas_lancamentos'][categoria_idx]
                    ['semanas'][semana_idx]['dias']).append({
                        'dia': valor_medicao.dia,
                        'campos': []
                    })
        cp_dias_dict = log_inicial['alteracoes'][alteracao_idx]['tabelas_lancamentos'][categoria_idx]
        cp_dias_dict = cp_dias_dict['semanas'][semana_idx]['dias'][-1]
    else:
        cp_dias_dict = lista_dias[0]
    dia_idx = cp_semana_dict['dias'].index(cp_dias_dict)
    return log_inicial, dia_idx, cp_dias_dict


def atualiza_ou_cria_nome_campo_log(lista_campos, log_inicial, alteracao_idx, categoria_idx,
                                    semana_idx, dia_idx, cp_dias_dict, valor_medicao, value):
    if not lista_campos:
        (log_inicial['alteracoes'][alteracao_idx]
                    ['tabelas_lancamentos'][categoria_idx]
                    ['semanas'][semana_idx]['dias'][dia_idx]
                    ['campos']).append({
                        'campo_nome': valor_medicao.nome_campo,
                        'de': valor_medicao.valor,
                        'para': value
                    })
        cp_campos_dict = log_inicial['alteracoes'][alteracao_idx]['tabelas_lancamentos'][categoria_idx]
        cp_campos_dict = cp_campos_dict['semanas'][semana_idx]['dias'][dia_idx]['campos'][-1]
    else:
        cp_campos_dict = lista_campos[0]
    campo_idx = cp_dias_dict['campos'].index(cp_campos_dict)
    return log_inicial, campo_idx, cp_campos_dict


def atualizar_log_escola_corrigiu(historico, log_inicial, medicao, dicionario_alteracoes, solicitacao):
    log_idx = historico.index(log_inicial)
    if medicao.periodo_escolar:
        periodo_nome = medicao.periodo_escolar.nome
    else:
        periodo_nome = medicao.grupo.nome

    lista_alteracoes = list(filter(lambda a: a['periodo_escolar'] == periodo_nome, log_inicial['alteracoes']))

    log_inicial, cp_alteracao_dict, alteracao_idx = get_alteracoes_log(lista_alteracoes,
                                                                       log_inicial,
                                                                       periodo_nome)
    for key, value in dicionario_alteracoes.items():
        valor_medicao = ValorMedicao.objects.get(uuid=key)
        log_inicial, cp_categorias_dict, categoria_idx = atualiza_ou_cria_tabela_lancamentos_log(valor_medicao,
                                                                                                 cp_alteracao_dict,
                                                                                                 log_inicial,
                                                                                                 alteracao_idx)

        lista_semanas = list(filter(lambda s: s['semana'] == valor_medicao.semana, cp_categorias_dict['semanas']))

        log_inicial, semana_idx, cp_semana_dict = atualiza_ou_cria_semanas_log(lista_semanas,
                                                                               log_inicial,
                                                                               alteracao_idx,
                                                                               categoria_idx,
                                                                               valor_medicao,
                                                                               cp_categorias_dict)

        lista_dias = list(filter(lambda dia: dia['dia'] == valor_medicao.dia, cp_semana_dict['dias']))

        log_inicial, dia_idx, cp_dias_dict = atualiza_ou_cria_dias_log(lista_dias,
                                                                       log_inicial,
                                                                       alteracao_idx,
                                                                       categoria_idx,
                                                                       semana_idx,
                                                                       valor_medicao,
                                                                       cp_semana_dict)

        lista_campos = list(filter(lambda c: c['campo_nome'] == valor_medicao.nome_campo, cp_dias_dict['campos']))

        log_inicial, campo_idx, cp_campos_dict = atualiza_ou_cria_nome_campo_log(lista_campos,
                                                                                 log_inicial,
                                                                                 alteracao_idx,
                                                                                 categoria_idx,
                                                                                 semana_idx,
                                                                                 dia_idx,
                                                                                 cp_dias_dict,
                                                                                 valor_medicao,
                                                                                 value)

        (historico[log_idx]['alteracoes'][alteracao_idx]
                  ['tabelas_lancamentos'][categoria_idx]
                  ['semanas'][semana_idx]['dias'][dia_idx]
                  ['campos'][campo_idx]['para']) = value
    solicitacao.historico = json.dumps(historico)
    solicitacao.save()


def log_alteracoes_escola_corrige_periodo(user, medicao, acao, data):
    solicitacao = medicao.solicitacao_medicao_inicial
    historico = json.loads(solicitacao.historico)
    log_inicial = encontrar_ou_criar_log_inicial(user, acao, historico)

    dicionario_alteracoes, valores_medicao = gerar_dicionario_e_buscar_valores_medicao(data, medicao)
    if not valores_medicao:
        return
    if not log_inicial['alteracoes']:
        criar_log_escola_corrigiu(medicao, valores_medicao, dicionario_alteracoes, log_inicial, historico, solicitacao)
    else:
        atualizar_log_escola_corrigiu(historico, log_inicial, medicao, dicionario_alteracoes, solicitacao)
