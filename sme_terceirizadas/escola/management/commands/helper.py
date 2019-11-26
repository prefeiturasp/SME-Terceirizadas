def calcula_total_alunos_por_escola(quest_json_data: dict) -> dict:
    escola_total = {}
    escolas_quantidades_alunos = quest_json_data['results']

    for escola_data in escolas_quantidades_alunos:
        codigo_escola = escola_data['cd_escola']
        total_corrente = escola_data['total']
        if codigo_escola not in escola_total:
            escola_total[codigo_escola] = total_corrente
        else:
            escola_total[codigo_escola] += total_corrente

    return escola_total
