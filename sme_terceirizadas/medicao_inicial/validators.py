from ..cardapio.models import VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
from ..dieta_especial.models import LogQuantidadeDietasAutorizadas
from ..escola.models import DiaCalendario
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoNormal
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


def comparar_dias_com_valores_medicao(valores_da_medicao, dias_letivos):
    if len(valores_da_medicao) != len(dias_letivos):
        return True
    else:
        return False


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
            log_por_classificacao = logs_por_periodo.filter(classificacao__nome=classificacao)
            for log in log_por_classificacao:
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
                    periodo_com_erro = comparar_dias_com_valores_medicao(valores_da_medicao, dias_letivos)
        if periodo_com_erro:
            lista_erros.append({
                'periodo_escolar': nome_periodo,
                'erro': 'Restam dias a serem lançados nas dietas.'
            })
    lista_erros = erros_unicos(lista_erros)
    return erros_unicos(lista_erros)
