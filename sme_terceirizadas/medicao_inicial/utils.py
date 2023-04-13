
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
