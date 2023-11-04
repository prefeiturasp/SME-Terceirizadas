import datetime
from django.db.models import Q

from ..cardapio.models import VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
from sme_terceirizadas.dados_comuns.utils import get_ultimo_dia_mes
from sme_terceirizadas.paineis_consolidados.utils import tratar_inclusao_continua
from ..dieta_especial.models import LogQuantidadeDietasAutorizadas
from ..escola.models import DiaCalendario
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua
from ..paineis_consolidados.models import SolicitacoesEscola
from sme_terceirizadas.paineis_consolidados.utils import formata_resultado_inclusoes_etec_autorizadas, tratar_data_evento_final_no_mes, tratar_dias_duplicados
from .models import CategoriaMedicao, ValorMedicao


def get_nome_campo(campo):
    campos = {
        'Matriculados': 'matriculados',
        'Frequência': 'frequencia',
        'Solicitado': 'solicitado',
        'Desjejum': 'desjejum',
        'Lanche': 'lanche',
        'Lanche 4h': 'lanche_4h',
        'Refeição': 'refeicao',
        'Repetição de Refeição': 'repeticao_refeicao',
        'Sobremesa': 'sobremesa',
        'Repetição de Sobremesa': 'repeticao_sobremesa',
    }
    return campos.get(campo, campo)


def get_alimentacao_nome_by_campo(campo):
    campos = {
        'matriculados': 'Matriculados',
        'frequencia': 'Frequência',
        'solicitado': 'Solicitado',
        'desjejum': 'Desjejum',
        'lanche': 'Lanche',
        'lanche_4h': 'Lanche 4h',
        'refeicao': 'Refeição',
        'repeticao_refeicao': 'Repetição de Refeição',
        'sobremesa': 'Sobremesa',
        'repeticao_sobremesa': 'Repetição de Sobremesa',
    }
    return campos.get(campo, campo)


def get_classificacoes_nomes(classificacao):
    categorias = {
        'Tipo A': 'DIETA ESPECIAL - TIPO A',
        'Tipo A - Restrição de aminoácidos': 'DIETA ESPECIAL - TIPO A - ENTERAL / RESTRIÇÃO DE AMINOÁCIDOS',
        'Tipo A Enteral': 'DIETA ESPECIAL - TIPO A - ENTERAL / RESTRIÇÃO DE AMINOÁCIDOS',
        'Tipo B': 'DIETA ESPECIAL - TIPO B'
    }
    return categorias.get(classificacao, classificacao)


def get_lista_dias_letivos(solicitacao, escola):
    dias_letivos = DiaCalendario.objects.filter(
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano),
        escola=escola,
        dia_letivo=True
    )
    dias_letivos = list(set(dias_letivos.values_list('data__day', flat=True)))
    return [str(dia) if not len(str(dia)) == 1 else ('0' + str(dia)) for dia in dias_letivos]


def erros_unicos(lista_erros):
    return list(map(dict, set(tuple(sorted(erro.items())) for erro in lista_erros)))


def buscar_valores_lancamento_alimentacoes(linhas_da_tabela, solicitacao,
                                           periodo_escolar, dias_letivos,
                                           categoria_medicao, lista_erros):
    periodo_com_erro = False
    for nome_campo in linhas_da_tabela:
        valores_da_medicao = ValorMedicao.objects.filter(
            medicao__solicitacao_medicao_inicial=solicitacao,
            nome_campo=nome_campo,
            medicao__periodo_escolar=periodo_escolar,
            dia__in=dias_letivos,
            categoria_medicao=categoria_medicao
        ).exclude(valor=None).values_list('dia', flat=True)
        valores_da_medicao = list(set(valores_da_medicao))
        if len(valores_da_medicao) != len(dias_letivos):
            diferenca = list(set(dias_letivos) - set(valores_da_medicao))
            for dia_sem_preenchimento in diferenca:
                valor_observacao = ValorMedicao.objects.filter(
                    medicao__solicitacao_medicao_inicial=solicitacao,
                    nome_campo='observacao',
                    medicao__periodo_escolar=periodo_escolar,
                    dia=dia_sem_preenchimento,
                    categoria_medicao=categoria_medicao
                ).exclude(valor=None)
                if not valor_observacao:
                    periodo_com_erro = True
    if periodo_com_erro:
        lista_erros.append({
            'periodo_escolar': periodo_escolar.nome,
            'erro': 'Restam dias a serem lançados nas alimentações.'
        })
    return lista_erros


def validate_lancamento_alimentacoes_medicao(solicitacao, lista_erros):
    escola = solicitacao.escola
    tipo_unidade = escola.tipo_unidade
    categoria_medicao = CategoriaMedicao.objects.get(nome='ALIMENTAÇÃO')
    dias_letivos = get_lista_dias_letivos(solicitacao, escola)
    for periodo_escolar in escola.periodos_escolares:
        vinculo = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.get(
            tipo_unidade_escolar=tipo_unidade,
            periodo_escolar=periodo_escolar
        )
        alimentacoes_vinculadas = vinculo.tipos_alimentacao.exclude(nome='Lanche Emergencial')
        alimentacoes_vinculadas = list(set(alimentacoes_vinculadas.values_list('nome', flat=True)))
        linhas_da_tabela = ['matriculados', 'frequencia']
        for alimentacao in alimentacoes_vinculadas:
            nome_formatado = get_nome_campo(alimentacao)
            linhas_da_tabela.append(nome_formatado)
            if nome_formatado == 'refeicao':
                linhas_da_tabela.append('repeticao_refeicao')
            if nome_formatado == 'sobremesa':
                linhas_da_tabela.append('repeticao_sobremesa')

        lista_erros = buscar_valores_lancamento_alimentacoes(linhas_da_tabela,
                                                             solicitacao,
                                                             periodo_escolar,
                                                             dias_letivos,
                                                             categoria_medicao,
                                                             lista_erros)
    return erros_unicos(lista_erros)


def buscar_valores_lancamento_inclusoes(inclusao, solicitacao, categoria_medicao, lista_erros):
    periodo_com_erro = False
    for nome_campo in inclusao['linhas_da_tabela']:
        valores_da_medicao = ValorMedicao.objects.filter(
            medicao__solicitacao_medicao_inicial=solicitacao,
            nome_campo=nome_campo,
            medicao__periodo_escolar__nome=inclusao['periodo_escolar'],
            dia=inclusao['dia'],
            categoria_medicao=categoria_medicao
        ).exclude(valor=None)
        if not valores_da_medicao:
            valor_observacao = ValorMedicao.objects.filter(
                medicao__solicitacao_medicao_inicial=solicitacao,
                nome_campo='observacao',
                medicao__periodo_escolar__nome=inclusao['periodo_escolar'],
                dia=inclusao['dia'],
                categoria_medicao=categoria_medicao
            ).exclude(valor=None)
            if not valor_observacao:
                periodo_com_erro = True
    if periodo_com_erro:
        lista_erros.append({
            'periodo_escolar': inclusao['periodo_escolar'],
            'erro': 'Restam dias a serem lançados nas alimentações.'
        })
    return lista_erros


def validate_lancamento_inclusoes(solicitacao, lista_erros):
    escola = solicitacao.escola
    categoria_medicao = CategoriaMedicao.objects.get(nome='ALIMENTAÇÃO')
    list_inclusoes = []

    inclusoes_uuids = list(set(GrupoInclusaoAlimentacaoNormal.objects.filter(
        escola=escola,
        status=GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO
    ).values_list('inclusoes_normais__uuid', flat=True)))
    inclusoes = InclusaoAlimentacaoNormal.objects.filter(
        uuid__in=inclusoes_uuids,
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano),
        cancelado=False
    ).order_by('data')

    for inclusao in inclusoes:
        grupo = inclusao.grupo_inclusao
        for periodo in grupo.quantidades_periodo.all():
            tipos_alimentacao = periodo.tipos_alimentacao.exclude(nome='Lanche Emergencial')
            tipos_alimentacao = list(set(tipos_alimentacao.values_list('nome', flat=True)))
            tipos_alimentacao = [get_nome_campo(alimentacao) for alimentacao in tipos_alimentacao]

            dia_da_inclusao = str(inclusao.data.day)
            if len(dia_da_inclusao) == 1:
                dia_da_inclusao = ('0' + str(inclusao.data.day))
            list_inclusoes.append({
                'periodo_escolar': periodo.periodo_escolar.nome,
                'dia': dia_da_inclusao,
                'linhas_da_tabela': tipos_alimentacao
            })
    for inclusao in list_inclusoes:
        lista_erros = buscar_valores_lancamento_inclusoes(inclusao, solicitacao,
                                                          categoria_medicao, lista_erros)
    return erros_unicos(lista_erros)


def get_alimentos_permitidos_por_dieta(dieta_especial):
    if dieta_especial.classificacao.nome in ['Tipo A', 'Tipo B']:
        return ['Lanche', 'Lanche 4h']
    else:
        return ['Lanche', 'Lanche 4h', 'Refeição']


def get_campos_por_periodo(periodo_da_escola, dieta_especial):
    nomes_campos = []
    nomes_alimentos = get_alimentos_permitidos_por_dieta(dieta_especial)
    tipos_alimentacao = periodo_da_escola.tipos_alimentacao.filter(nome__in=nomes_alimentos)
    tipos_alimentacao = tipos_alimentacao.values_list('nome', flat=True)
    nomes_campos = [get_nome_campo(alimentacao) for alimentacao in tipos_alimentacao]
    return nomes_campos


def comparar_dias_com_valores_medicao(valores_da_medicao, dias_letivos, quantidade_dias_letivos_sem_log):
    return len(valores_da_medicao) != (len(dias_letivos) - quantidade_dias_letivos_sem_log)


def get_quantidade_dias_letivos_sem_log(dias_letivos, logs_por_classificacao):
    logs = [f'{log.data.day:02d}' for log in logs_por_classificacao.filter(data__day__in=dias_letivos)]
    return len(set(dias_letivos) - set(logs))


def validate_lancamento_dietas(solicitacao, lista_erros):
    escola = solicitacao.escola
    periodos_da_escola = escola.periodos_escolares.all()
    log_dietas_especiais = LogQuantidadeDietasAutorizadas.objects.filter(
        escola=escola,
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano)
    ).exclude(periodo_escolar=None).exclude(quantidade=0).exclude(classificacao__nome='Tipo C')

    nomes_campos_padrao = ['dietas_autorizadas', 'frequencia']
    dias_letivos = get_lista_dias_letivos(solicitacao, escola)

    nomes_dos_periodos = log_dietas_especiais.order_by('periodo_escolar__nome')
    nomes_dos_periodos = nomes_dos_periodos.values_list('periodo_escolar__nome', flat=True)
    nomes_dos_periodos = nomes_dos_periodos.distinct()

    for nome_periodo in nomes_dos_periodos:
        periodo_com_erro = False
        nomes_campos = []
        periodo_da_escola = periodos_da_escola.get(nome=nome_periodo)
        logs_por_periodo = log_dietas_especiais.filter(periodo_escolar=periodo_da_escola)
        classificacoes = log_dietas_especiais.order_by('classificacao__nome')
        classificacoes = classificacoes.values_list('classificacao__nome', flat=True)
        classificacoes = classificacoes.distinct()
        for classificacao in classificacoes:
            logs_por_classificacao = logs_por_periodo.filter(classificacao__nome=classificacao)
            quantidade_dias_letivos_sem_log = get_quantidade_dias_letivos_sem_log(
                dias_letivos, logs_por_classificacao)
            for log in logs_por_classificacao:
                nomes_campos = get_campos_por_periodo(periodo_da_escola, log)
                nomes_campos = nomes_campos + nomes_campos_padrao
                for nome_campo in nomes_campos:
                    valores_da_medicao = ValorMedicao.objects.filter(
                        medicao__solicitacao_medicao_inicial=solicitacao,
                        nome_campo=nome_campo,
                        medicao__periodo_escolar__nome=nome_periodo,
                        dia__in=dias_letivos,
                        categoria_medicao__nome=get_classificacoes_nomes(classificacao)
                    ).order_by('dia').exclude(valor=None).values_list('dia', flat=True)
                    valores_da_medicao = list(set(valores_da_medicao))
                    periodo_com_erro = comparar_dias_com_valores_medicao(
                        valores_da_medicao, dias_letivos, quantidade_dias_letivos_sem_log)
        if periodo_com_erro:
            lista_erros.append({
                'periodo_escolar': nome_periodo,
                'erro': 'Restam dias a serem lançados nas dietas.'
            })
    lista_erros = erros_unicos(lista_erros)
    return erros_unicos(lista_erros)


def remover_duplicados(query_set):
    aux = []
    sem_uuid_repetido = []
    for resultado in query_set:
        if resultado.uuid not in aux:
            aux.append(resultado.uuid)
            sem_uuid_repetido.append(resultado)
    return sem_uuid_repetido


def formatar_query_set_alteracao(query_set, mes, ano):
    datas = []
    for alteracao_alimentacao in query_set:
        alteracao = alteracao_alimentacao.get_raw_model.objects.get(uuid=alteracao_alimentacao.uuid)
        datas_intervalos = alteracao.datas_intervalo.filter(data__month=mes, data__year=ano, cancelado=False)
        for obj in datas_intervalos:
            if not len(str(obj.data.day)) == 1:
                datas.append(str(obj.data.day))
            else:
                datas.append(('0' + str(obj.data.day)))
    return list(set(datas))


def get_lista_dias_solicitacoes(params, escola):
    query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola.uuid)
    query_set = SolicitacoesEscola.busca_filtro(query_set, params)
    query_set = query_set.filter(data_evento__month=params['mes'], data_evento__year=params['ano'])
    query_set = query_set.filter(data_evento__lt=datetime.date.today())
    if params.get('eh_lanche_emergencial', False):
        query_set = query_set.filter(motivo__icontains='Emergencial')
        query_set = remover_duplicados(query_set)
        return formatar_query_set_alteracao(query_set, params['mes'], params['ano'])
    else:
        query_set = remover_duplicados(query_set)
        datas_kits = []
        for obj in query_set:
            if not len(str(obj.data_evento.day)) == 1:
                datas_kits.append(str(obj.data_evento.day))
            else:
                datas_kits.append(('0' + str(obj.data_evento.day)))
        return datas_kits


def validate_lancamento_kit_lanche(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    tipo_solicitacao = 'Kit Lanche'
    params = {
        'mes': mes, 'ano': ano,
        'escola_uuid': escola.uuid,
        'tipo_solicitacao': tipo_solicitacao
    }
    dias_kit_lanche = get_lista_dias_solicitacoes(params, escola)

    valores_da_medicao = ValorMedicao.objects.filter(
        medicao__solicitacao_medicao_inicial=solicitacao,
        nome_campo='kit_lanche',
        medicao__grupo__nome='Solicitações de Alimentação',
        dia__in=dias_kit_lanche,
    ).order_by('dia').exclude(valor=None).values_list('dia', flat=True)
    valores_da_medicao = list(set(valores_da_medicao))
    if len(valores_da_medicao) != len(dias_kit_lanche):
        lista_erros.append({
            'periodo_escolar': 'Solicitações de Alimentação',
            'erro': 'Restam dias a serem lançados nos Kit Lanches.'
        })
    return erros_unicos(lista_erros)


def validate_lanche_emergencial(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    tipo_solicitacao = 'Alteração'
    eh_lanche_emergencial = True

    params = {
        'mes': mes, 'ano': ano,
        'escola_uuid': escola.uuid,
        'tipo_solicitacao': tipo_solicitacao,
        'eh_lanche_emergencial': eh_lanche_emergencial
    }
    dias_lanche_emergencial = get_lista_dias_solicitacoes(params, escola)

    valores_da_medicao = ValorMedicao.objects.filter(
        medicao__solicitacao_medicao_inicial=solicitacao,
        nome_campo='lanche_emergencial',
        medicao__grupo__nome='Solicitações de Alimentação',
        dia__in=dias_lanche_emergencial,
    ).order_by('dia').exclude(valor=None).values_list('dia', flat=True)
    valores_da_medicao = list(set(valores_da_medicao))
    if len(valores_da_medicao) != len(dias_lanche_emergencial):
        lista_erros.append({
            'periodo_escolar': 'Solicitações de Alimentação',
            'erro': 'Restam dias a serem lançados nos Lanches Emergenciais.'
        })
    return erros_unicos(lista_erros)


def validate_solicitacoes_etec(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    tipo_solicitacao = 'Inclusão de'

    params = {
        'mes': mes, 'ano': ano,
        'escola_uuid': escola.uuid,
        'tipo_solicitacao': tipo_solicitacao,
    }

    date = datetime.date(int(ano), int(mes), 1)
    query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola.uuid)
    query_set = SolicitacoesEscola.busca_filtro(query_set, params)
    query_set = query_set.filter(
        Q(data_evento__month=mes, data_evento__year=ano) |
        Q(data_evento__lt=date, data_evento_2__gte=date)
    )
    query_set = query_set.filter(
        data_evento__lt=datetime.date.today(),
        motivo='ETEC'
    )

    query_set = remover_duplicados(query_set)

    return_dict = []
    periodo_com_erro = False

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

    for inclusao in tratar_dias_duplicados(return_dict):
        tipos_de_alimentacao = inclusao['tipos_alimentacao']
        if 'Refeição' in tipos_de_alimentacao:
            tipos_de_alimentacao.append('Repetição de Refeição')
        if 'Sobremesa' in tipos_de_alimentacao:
            tipos_de_alimentacao.append('Repetição de Sobremesa')

        for alimentacao in inclusao['tipos_alimentacao']:
            valores_da_medicao = ValorMedicao.objects.filter(
                medicao__solicitacao_medicao_inicial=solicitacao,
                nome_campo=get_nome_campo(alimentacao),
                medicao__grupo__nome='ETEC',
                dia=inclusao['dia'],
                categoria_medicao__nome='ALIMENTAÇÃO'
            )
            if not valores_da_medicao:
                periodo_com_erro = True
    if periodo_com_erro:
        lista_erros.append({
            'periodo_escolar': 'ETEC',
            'erro': 'Restam dias a serem lançados nas alimentações.'
        })
    return erros_unicos(lista_erros)


def get_inclusoes_programas_projetos(escola, mes, ano):
    nome_motivos = ['Programas/Projetos Contínuos', 'Programas/Projetos Específicos']
    primeiro_dia_mes = datetime.date(int(ano), int(mes), 1)
    ultimo_dia_mes = get_ultimo_dia_mes(primeiro_dia_mes)

    inclusoes = InclusaoAlimentacaoContinua.objects.filter(
        status='CODAE_AUTORIZADO',
        rastro_escola=escola
    )
    inclusoes = inclusoes.filter(
        data_inicial__lte=ultimo_dia_mes,
        data_final__gte=primeiro_dia_mes,
    )

    return inclusoes.filter(motivo__nome__in=nome_motivos)


def validar_dietas_programas_projetos(return_dict, log_dietas_especiais, solicitacao, periodo_com_erro_dieta):
    nomes_campos_padrao = ['dietas_autorizadas', 'frequencia']
    for inclusao in return_dict:
        dietas_nas_inclusoes = log_dietas_especiais.filter(data__day=int(inclusao['dia']))
        for log in dietas_nas_inclusoes:
            periodo_escolar = solicitacao.escola.periodos_escolares.get(nome=inclusao['periodo'])
            nomes_campos = []
            nomes_campos = get_campos_por_periodo(periodo_escolar, log)
            nomes_campos = nomes_campos_padrao + nomes_campos
            for nome_campo in nomes_campos:
                valores_da_medicao = ValorMedicao.objects.filter(
                    medicao__solicitacao_medicao_inicial=solicitacao,
                    nome_campo=get_nome_campo(nome_campo),
                    medicao__grupo__nome='Programas e Projetos',
                    dia=inclusao['dia'],
                    categoria_medicao__nome=get_classificacoes_nomes(log.classificacao.nome)
                )
            if not valores_da_medicao:
                periodo_com_erro_dieta = True
    return periodo_com_erro_dieta


def validar_dias_inclusoes_programas_projetos(return_dict, escola, solicitacao, periodo_com_erro):
    nomes_campos_padrao = ['numero_de_alunos', 'frequencia']
    tipo_unidade = escola.tipo_unidade
    for inclusao in return_dict:
        periodo_escolar = escola.periodos_escolares.get(nome=inclusao['periodo'])
        vinculo = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.get(
            tipo_unidade_escolar=tipo_unidade,
            periodo_escolar=periodo_escolar
        )
        alimentacoes_vinculadas = vinculo.tipos_alimentacao.exclude(nome='Lanche Emergencial')
        lista_alimentacoes_inclusao = inclusao['alimentacoes'].split(', ')
        lista_alimentacoes_inclusao = [get_alimentacao_nome_by_campo(a) for a in lista_alimentacoes_inclusao]
        alimentacoes_vinculadas = alimentacoes_vinculadas.filter(nome__in=lista_alimentacoes_inclusao)
        alimentacoes_vinculadas = alimentacoes_vinculadas.values_list('nome', flat=True)

        for alimentacao in alimentacoes_vinculadas:
            nome_formatado = get_nome_campo(alimentacao)
            nomes_campos_padrao.append(nome_formatado)
            if nome_formatado == 'refeicao':
                nomes_campos_padrao.append('repeticao_refeicao')
            if nome_formatado == 'sobremesa':
                nomes_campos_padrao.append('repeticao_sobremesa')

        for nome_campo in nomes_campos_padrao:
            valores_da_medicao = ValorMedicao.objects.filter(
                medicao__solicitacao_medicao_inicial=solicitacao,
                nome_campo=get_nome_campo(nome_campo),
                medicao__grupo__nome='Programas e Projetos',
                dia=inclusao['dia'],
                categoria_medicao__nome='ALIMENTAÇÃO'
            )
            if not valores_da_medicao:
                periodo_com_erro = True
    return periodo_com_erro


def validate_solicitacoes_programas_e_projetos(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    inclusoes = get_inclusoes_programas_projetos(escola, mes, ano)
    return_dict = []
    periodo_com_erro = False
    periodo_com_erro_dieta = False

    if not inclusoes:
        return lista_erros

    for inclusao in inclusoes:
        for periodo in inclusao.quantidades_periodo.all():
            if not periodo.cancelado:
                inc = SolicitacoesEscola.objects.filter(uuid=inclusao.uuid)
                inc = remover_duplicados(inc)[0]
                tratar_inclusao_continua(mes, ano, periodo, inc, return_dict)

    dias_inclusoes = [int(d['dia']) for d in return_dict]

    log_dietas_especiais = LogQuantidadeDietasAutorizadas.objects.filter(
        escola__uuid=escola.uuid,
        data__day__in=dias_inclusoes,
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano),
        periodo_escolar=None
    ).exclude(quantidade=0).exclude(classificacao__nome='Tipo C')

    periodo_com_erro_dieta = validar_dietas_programas_projetos(
        return_dict, log_dietas_especiais, solicitacao,
        periodo_com_erro_dieta
    )

    periodo_com_erro = validar_dias_inclusoes_programas_projetos(
        return_dict, escola, solicitacao,
        periodo_com_erro
    )

    if periodo_com_erro_dieta:
        lista_erros.append({
            'periodo_escolar': 'Programas e Projetos',
            'erro': 'Restam dias a serem lançados nas dietas.'
        })

    if periodo_com_erro:
        lista_erros.append({
            'periodo_escolar': 'Programas e Projetos',
            'erro': 'Restam dias a serem lançados nas alimentações.'
        })
    return erros_unicos(lista_erros)
