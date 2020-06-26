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
