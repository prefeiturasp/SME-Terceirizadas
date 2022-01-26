import logging
import re
from datetime import date, datetime

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
    from sme_terceirizadas.escola.models import (
        AlunosMatriculadosPeriodoEscola,
        Escola
    )
    hoje = date.today()
    escolas = Escola.objects.all()
    total = len(escolas)
    cont = 1
    AlunosMatriculadosPeriodoEscola.objects.filter(tipo_turma=tipo_turma.name).delete()
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


def processa_dias_letivos(lista_dias_letivos, escola):
    from sme_terceirizadas.escola.models import DiaCalendario

    for dia_dict in lista_dias_letivos:
        data = datetime.strptime(dia_dict['data'], '%Y-%m-%dT00:00:00')
        dia_calendario: DiaCalendario = DiaCalendario.objects.filter(escola=escola, data__year=data.year,
                                                                     data__month=data.month, data__day=data.day).first()
        if not dia_calendario:
            dia_calendario = DiaCalendario.objects.create(
                escola=escola,
                data=data,
                dia_letivo=dia_dict['ehLetivo']
            )
        else:
            dia_calendario.dia_letivo = dia_dict['ehLetivo']
            dia_calendario.save()


def calendario_sgp():
    from calendar import monthrange

    from sme_terceirizadas.escola.models import Escola
    from sme_terceirizadas.escola.services import NovoSGPServico

    hoje = date.today()
    escolas = Escola.objects.all()
    total = len(escolas)
    for cont, escola in enumerate(escolas, 1):
        logger.debug(f'Processando {cont} de {total}')
        logger.debug(f"""Consultando dias letivos da escola com Nome: {escola.nome}
        e código eol: {escola.codigo_eol}, data: {hoje.strftime('%Y-%m-%d')}""")
        try:
            ultimo_dia_do_mes_atual = monthrange(year=hoje.year, month=hoje.month)[1]
            data_inicio = hoje.strftime('%Y-%m-%d')
            data_fim = datetime(year=hoje.year, month=hoje.month, day=ultimo_dia_do_mes_atual).strftime('%Y-%m-%d')

            resposta = NovoSGPServico.dias_letivos(
                codigo_eol=escola.codigo_eol,
                data_inicio=data_inicio,
                data_fim=data_fim)
            logger.debug(resposta)

            processa_dias_letivos(resposta, escola)
        except Exception as e:
            logger.error(f'Dados não encontrados para escola {escola} : {str(e)}')
            logger.debug('Tentando buscar dias letivos no novo sgp para turno da noite')
            resposta = NovoSGPServico.dias_letivos(
                codigo_eol=escola.codigo_eol,
                data_inicio=data_inicio,
                data_fim=data_fim,
                tipo_turno=3)

            processa_dias_letivos(resposta, escola)


class EscolaSimplissimaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
