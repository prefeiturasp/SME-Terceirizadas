import logging
import re

from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger('sigpae.taskEscola')


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


def remove_acentos(texto):
    resultado = re.sub(u'[àáâãäå]', 'a', texto)
    resultado = re.sub(u'[èéêë]', 'e', resultado)
    resultado = re.sub(u'[ìíîï]', 'i', resultado)
    return resultado


def registra_quantidade_matriculados(turnos, escola, data):
    from sme_terceirizadas.escola.models import (
        AlunosMatriculadosPeriodoEscolaRegular,
        LogAlunosMatriculadosPeriodoEscolaRegular,
        PeriodoEscolar
    )

    for turno_resp in turnos:
        turno = remove_acentos(turno_resp['turno'])
        periodo = PeriodoEscolar.objects.filter(nome=turno.upper()).first()
        if not periodo:
            logger.debug(f'Periodo {turno_resp["turno"]} não encontrado na tabela de Períodos')
            continue

        AlunosMatriculadosPeriodoEscolaRegular.criar(
            escola=escola, periodo_escolar=periodo, quantidade_alunos=turno_resp['quantidade'])

        LogAlunosMatriculadosPeriodoEscolaRegular.criar(
            escola=escola, periodo_escolar=periodo, quantidade_alunos=turno_resp['quantidade'],
            data=data)


class EscolaSimplissimaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
