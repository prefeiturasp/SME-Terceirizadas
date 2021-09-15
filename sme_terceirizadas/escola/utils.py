import logging
import re
from datetime import date

from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.eol_servico.utils import EOLServicoSGP

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


def registra_quantidade_matriculados(turnos, escola, data, tipo_turma):
    from sme_terceirizadas.escola.models import (
        AlunosMatriculadosPeriodoEscola,
        LogAlunosMatriculadosPeriodoEscola,
        PeriodoEscolar
    )

    for turno_resp in turnos:
        turno = remove_acentos(turno_resp['turno'])
        periodo = PeriodoEscolar.objects.filter(nome=turno.upper()).first()
        if not periodo:
            logger.debug(f'Periodo {turno_resp["turno"]} não encontrado na tabela de Períodos')
            continue

        AlunosMatriculadosPeriodoEscola.criar(
            escola=escola, periodo_escolar=periodo,
            quantidade_alunos=turno_resp['quantidade'],
            tipo_turma=tipo_turma)

        LogAlunosMatriculadosPeriodoEscola.criar(
            escola=escola, periodo_escolar=periodo,
            quantidade_alunos=turno_resp['quantidade'],
            data=data, tipo_turma=tipo_turma)


def registro_quantidade_alunos_matriculados_por_escola_periodo(tipo_turma):
    from sme_terceirizadas.escola.models import Escola

    hoje = date.today()
    escolas = Escola.objects.all()
    total = len(escolas)
    cont = 1
    for escola in escolas:
        logger.debug(f'Processando {cont} de {total}')
        logger.debug(f"""Consultando matriculados da escola com Nome: {escola.nome}
        e código eol: {escola.codigo_eol}, data: {hoje.strftime('%Y-%m-%d')} para o tipo turma {tipo_turma.name}""")
        try:
            resposta = EOLServicoSGP.matricula_por_escola(
                codigo_eol=escola.codigo_eol,
                data=hoje.strftime('%Y-%m-%d'),
                tipo_turma=tipo_turma.value)
            logger.debug(resposta)

            registra_quantidade_matriculados(resposta['turnos'], escola, hoje, tipo_turma.name)
        except Exception as e:
            logger.error(f'Dados não encontrados para escola {escola} : {str(e)}')
        cont += 1


class EscolaSimplissimaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
