def meses_para_mes_e_ano_string(meses):
    anos = meses // 12
    meses = meses % 12

    saida = ''

    if anos > 0:
        saida = f'{anos} ' + ('ano' if anos == 1 else 'anos')
        if meses > 0:
            saida += ' e '
    if anos == 0 or meses > 0:
        saida += f'{meses} ' + ('mês' if meses == 1 else 'meses')

    return saida
