from datetime import datetime, timedelta


def agrupa_por_terceirizada(queryset):  # noqa C901
    agrupado = []
    produtos_atual = []
    total_produtos = 0
    ultima_terceirizada = None

    sorted_queryset = sorted(
        queryset,
        key=lambda i: i.criado_por.vinculo_atual.instituicao.nome.lower())

    for produto in sorted_queryset:
        if ultima_terceirizada is None:
            ultima_terceirizada = produto.criado_por.vinculo_atual.instituicao
            produtos_atual = [produto]
        elif ultima_terceirizada != produto.criado_por.vinculo_atual.instituicao:
            agrupado.append({
                'terceirizada': ultima_terceirizada,
                'produtos': produtos_atual
            })
            total_produtos += len(produtos_atual)
            ultima_terceirizada = produto.criado_por.vinculo_atual.instituicao
            produtos_atual = [produto]
        else:
            produtos_atual.append(produto)

    if len(produtos_atual) > 0:
        agrupado.append({
            'terceirizada': ultima_terceirizada,
            'produtos': produtos_atual
        })
        total_produtos += len(produtos_atual)

    return {
        'results': agrupado,
        'total_produtos': total_produtos
    }

def cria_filtro_produto_por_parametros_form(cleaned_data):  # noqa C901
    campos_a_pesquisar = {}
    for (chave, valor) in cleaned_data.items():
        if valor != '' and valor is not None:
            if chave == 'uuid':
                campos_a_pesquisar['homologacoes__uuid'] = valor
            if chave == 'nome_fabricante':
                campos_a_pesquisar['fabricante__nome__icontains'] = valor
            elif chave == 'nome_marca':
                campos_a_pesquisar['marca__nome__icontains'] = valor
            elif chave == 'nome_produto':
                campos_a_pesquisar['nome__icontains'] = valor
            elif chave == 'nome_terceirizada':
                campos_a_pesquisar['homologacoes__rastro_terceirizada__nome_fantasia__icontains'] = valor
            elif chave == 'data_inicial':
                campos_a_pesquisar['homologacoes__criado_em__gte'] = valor
            elif chave == 'data_final':
                campos_a_pesquisar['homologacoes__criado_em__lt'] = valor + timedelta(days=1)
            elif chave == 'status' and len(valor) > 0:
                campos_a_pesquisar['homologacoes__status__in'] = valor

    return campos_a_pesquisar


def converte_para_datetime(data):
    if data:
        return datetime.strptime(data, '%d/%m/%Y')
    return None


def get_filtros_data_range(data_analise_inicial, data_analise_final):
    filtros_data = {}
    if data_analise_inicial == data_analise_final:
        filtros_data['criado_em__date'] = data_analise_inicial
    else:
        filtros_data['criado_em__range'] = (data_analise_inicial, data_analise_final + timedelta(days=1))
    return filtros_data


def get_filtros_data_em_analise_sensorial(data_analise_inicial, data_analise_final):

    if data_analise_inicial and data_analise_final:
        filtros_data = get_filtros_data_range(data_analise_inicial, data_analise_final)

    else:
        filtros_data = {}
        if data_analise_inicial:
            filtros_data['criado_em__gte'] = data_analise_inicial

        if data_analise_final:
            filtros_data['criado_em__lte'] = data_analise_final + timedelta(days=1)
    return filtros_data
