from rest_framework import serializers

from sme_terceirizadas.escola.models import EscolaPeriodoEscolar

from ..models import InclusaoAlimentacaoDaCEI


def retorna_quantidades_de_alunos(faixas_etarias_da_inclusao, faixa_alunos_inclusoes):
    for item in faixas_etarias_da_inclusao:
        encontrou = faixa_alunos_inclusoes.get(item.faixa_etaria.uuid, False)
        if not encontrou:
            faixa_alunos_inclusoes[
                item.faixa_etaria.uuid] = item.quantidade_alunos
        else:
            faixa_alunos_inclusoes[
                item.faixa_etaria.uuid] += item.quantidade_alunos
    return faixa_alunos_inclusoes


def verifica_se_excedeu_o_limite(faixa_alunos_inclusoes, quantidades_dos_alunos, uuid_faixa, faixa_alunos):
    for qtd_aluno in quantidades_dos_alunos:
        if qtd_aluno['faixa_etaria'].uuid == uuid_faixa:
            if faixa_alunos_inclusoes[uuid_faixa] + qtd_aluno['quantidade_alunos'] > faixa_alunos[uuid_faixa]:
                raise serializers.ValidationError('quantidades de alunos excedidas')
    return True


def valida_quantidade_de_alunos_nas_faixas_etarias(quantidades_dos_alunos, escola, dia_solicitacao, periodo_escolar):
    inclusoes = InclusaoAlimentacaoDaCEI.objects.filter(
        data=dia_solicitacao,
        escola=escola
    )

    escola_periodo = EscolaPeriodoEscolar.objects.get(
        escola=escola,
        periodo_escolar=periodo_escolar
    )

    faixa_alunos_inclusoes = {}
    for inclusao in inclusoes:
        faixas_etarias_da_inclusao = inclusao.quantidade_alunos_por_faixas_etarias.all()
        faixa_alunos_inclusoes.update(
            retorna_quantidades_de_alunos(faixas_etarias_da_inclusao, faixa_alunos_inclusoes)
        )

    faixa_alunos = escola_periodo.alunos_por_faixa_etaria(dia_solicitacao)

    for uuid_faixa in faixa_alunos:
        if faixa_alunos_inclusoes.get(uuid_faixa, False):
            verifica_se_excedeu_o_limite(faixa_alunos_inclusoes, quantidades_dos_alunos, uuid_faixa, faixa_alunos)
    return True
