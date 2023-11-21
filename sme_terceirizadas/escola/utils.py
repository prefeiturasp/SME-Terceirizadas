import logging
import re
from datetime import date, datetime, timedelta

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.eol_servico.utils import EOLServicoSGP

logger = logging.getLogger('sigpae.taskEscola')


def meses_to_mes_e_ano_string(total_meses):
    anos = total_meses // 12
    meses = total_meses % 12

    saida = ''

    if anos > 0:
        saida = f"{anos:02d} {'ano' if anos == 1 else 'anos'}"
        if meses > 0:
            saida += ' e '

    if anos == 0 or meses > 0:
        saida += f"{meses:02d} {'mês' if meses == 1 else 'meses'}"

    return saida


def faixa_to_string(inicio, fim):
    if fim - inicio == 1:
        return meses_to_mes_e_ano_string(inicio)
    if inicio == 0:
        str_inicio = '0 meses'
    else:
        str_inicio = meses_to_mes_e_ano_string(inicio) if inicio >= 12 else f'{inicio:02d}'
    str_fim = '06 anos' if fim == 72 else meses_to_mes_e_ano_string(fim - 1)

    return f'{str_inicio} a {str_fim}'


def string_to_faixa(faixa_str):
    if 'a' in faixa_str:
        str_inicio, str_fim = faixa_str.split(' a ')
    else:
        str_inicio = str_fim = faixa_str

    inicio = string_to_meses(str_inicio)
    fim = string_to_meses(str_fim) + 1  # Adicionamos 1 porque a função faixa_to_string subtrai 1 do fim

    return inicio, fim


def string_to_meses(str_meses):
    if 'ano' in str_meses:
        anos, restante = str_meses.split(' ano')
        anos = int(anos)
        meses = 0
        if ' e ' in restante:
            _, str_mes = restante.split(' e ')
            meses = int(str_mes.split(' ')[0])
        total_meses = anos * 12 + meses
    else:
        total_meses = int(str_meses.split(' ')[0])
    return total_meses


def remove_acentos(texto):
    resultado = re.sub(u'[àáâãäå]', 'a', texto)
    resultado = re.sub(u'[èéêë]', 'e', resultado)
    resultado = re.sub(u'[ìíîï]', 'i', resultado)
    return resultado


def update_datetime_LogAlunosMatriculadosPeriodoEscola():
    from sme_terceirizadas.escola.models import (
        LogAlunosMatriculadosPeriodoEscola,
    )
    hoje = date.today()
    logs_hoje = LogAlunosMatriculadosPeriodoEscola.objects.filter(criado_em__date=hoje)

    for log in logs_hoje:
        log.criado_em = log.criado_em - timedelta(days=1)
        log.save()


def registra_quantidade_matriculados(matriculas, ontem, tipo_turma):  # noqa C901
    from sme_terceirizadas.escola.models import (
        AlunosMatriculadosPeriodoEscola,
        LogAlunosMatriculadosPeriodoEscola,
        PeriodoEscolar,
        Escola
    )
    import ast
    import pandas as pd
    objs = []
    matriculas = pd.DataFrame(matriculas).astype(str).drop_duplicates().to_dict('records')
    for matricula in matriculas:
        escola = Escola.objects.filter(codigo_eol=matricula['codigoEolEscola']).first()
        turnos = ast.literal_eval(matricula['turnos'])
        periodos = []
        for turno_resp in turnos:
            turno = remove_acentos(turno_resp['turno'])
            periodo = PeriodoEscolar.objects.filter(nome=turno.upper()).first()
            if not periodo:
                logger.debug(f'Periodo {turno_resp["turno"]} não encontrado na tabela de Períodos')
                continue
            periodos.append(periodo)
            if tipo_turma == 'REGULAR':
                create_update_objeto_escola_periodo_escolar(escola, periodo, turno_resp['quantidade'])
            matricula_sigpae = AlunosMatriculadosPeriodoEscola.objects.filter(tipo_turma=tipo_turma,
                                                                              escola=escola,
                                                                              periodo_escolar=periodo).first()
            if matricula_sigpae:
                matricula_sigpae.quantidade_alunos = turno_resp['quantidade']
                objs.append(matricula_sigpae)
            else:
                AlunosMatriculadosPeriodoEscola.criar(
                    escola=escola,
                    periodo_escolar=periodo,
                    quantidade_alunos=turno_resp['quantidade'],
                    tipo_turma=tipo_turma)
            LogAlunosMatriculadosPeriodoEscola.criar(
                escola=escola,
                periodo_escolar=periodo,
                quantidade_alunos=turno_resp['quantidade'],
                data=ontem,
                tipo_turma=tipo_turma)

        AlunosMatriculadosPeriodoEscola.objects.filter(
            tipo_turma=tipo_turma,
            escola=escola
        ).exclude(periodo_escolar__in=periodos).delete()
    AlunosMatriculadosPeriodoEscola.objects.bulk_update(objs, ['quantidade_alunos'])
    update_datetime_LogAlunosMatriculadosPeriodoEscola()


def create_update_objeto_escola_periodo_escolar(escola, periodo, quantidade_alunos_periodo):
    from sme_terceirizadas.escola.models import EscolaPeriodoEscolar
    escola_periodo, created = EscolaPeriodoEscolar.objects.get_or_create(
        periodo_escolar=periodo, escola=escola
    )
    if escola_periodo.quantidade_alunos != quantidade_alunos_periodo:
        escola_periodo.quantidade_alunos = quantidade_alunos_periodo
        escola_periodo.save()


def duplica_dia_anterior(dre, dois_dias_atras, ontem, tipo_turma_name):
    from sme_terceirizadas.escola.models import (
        LogAlunosMatriculadosPeriodoEscola,
    )
    logs = LogAlunosMatriculadosPeriodoEscola.objects.filter(escola__diretoria_regional=dre,
                                                             criado_em__date=dois_dias_atras,
                                                             tipo_turma=tipo_turma_name)
    for log in logs:
        LogAlunosMatriculadosPeriodoEscola.criar(
            escola=log.escola, periodo_escolar=log.periodo_escolar,
            quantidade_alunos=log.quantidade_alunos,
            data=ontem, tipo_turma=tipo_turma_name)
    update_datetime_LogAlunosMatriculadosPeriodoEscola()


def registro_quantidade_alunos_matriculados_por_escola_periodo(tipo_turma):
    from sme_terceirizadas.escola.models import (
        DiretoriaRegional
    )
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    dres = DiretoriaRegional.objects.all()
    total = len(dres)
    cont = 1
    for dre in dres:
        logger.debug(f'Processando {cont} de {total}')
        logger.debug(f"""Consultando matriculados da dre com Nome: {dre.nome}
        e código eol: {dre.codigo_eol}, data: {hoje.strftime('%Y-%m-%d')} para o tipo turma {tipo_turma.name}""")
        try:
            resposta = EOLServicoSGP.matricula_por_escola(
                codigo_eol=dre.codigo_eol,
                data=hoje.strftime('%Y-%m-%d'),
                tipo_turma=tipo_turma.value)
            logger.debug(resposta)

            registra_quantidade_matriculados(resposta, ontem, tipo_turma.name)
        except Exception as e:
            dois_dias_atras = ontem - timedelta(days=1)
            duplica_dia_anterior(dre, dois_dias_atras, ontem, tipo_turma.name)
            logger.error(f'Houve um erro inesperado ao consultar a Diretoria Regional {dre} : {str(e)}; '
                         f'as quantidades de alunos foram duplicadas do dia anterior')
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


def calendario_sgp():  # noqa C901
    import pandas as pd

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
            data_inicio = hoje.strftime('%Y-%m-%d')
            data_final = (hoje + pd.DateOffset(months=3)).date()
            data_fim = data_final.strftime('%Y-%m-%d')

            resposta = NovoSGPServico.dias_letivos(
                codigo_eol=escola.codigo_eol,
                data_inicio=data_inicio,
                data_fim=data_fim)
            logger.debug(resposta)

            processa_dias_letivos(resposta, escola)
        except Exception as e:
            logger.error(f'Dados não encontrados para escola {escola} : {str(e)}')
            logger.debug('Tentando buscar dias letivos no novo sgp para turno da noite')
            try:
                resposta = NovoSGPServico.dias_letivos(
                    codigo_eol=escola.codigo_eol,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    tipo_turno=3)

                processa_dias_letivos(resposta, escola)
            except Exception as e:
                logger.error(f'Erro ao buscar por turno noite para escola {escola} : {str(e)}')


class EscolaSimplissimaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


def lotes_endpoint_filtrar_relatorio_alunos_matriculados(instituicao, Codae, Lote):
    if isinstance(instituicao, Codae):
        lotes = Lote.objects.all()
    else:
        lotes = instituicao.lotes.filter(escolas__isnull=False)
    return lotes


def deletar_alunos_periodo_parcial_outras_escolas(escola, data_referencia):
    from .models import AlunoPeriodoParcial
    AlunoPeriodoParcial.objects.filter(
        solicitacao_medicao_inicial__escola=escola,
        solicitacao_medicao_inicial__mes=str(data_referencia.month).zfill(2),
        solicitacao_medicao_inicial__ano=str(data_referencia.year)
    ).exclude(aluno__escola__codigo_eol=escola.codigo_eol).delete()


def eh_dia_sem_atividade_escolar(escola, data, alteracao):
    from sme_terceirizadas.escola.models import DiaCalendario, DiaSuspensaoAtividades
    try:
        dia_calendario = DiaCalendario.objects.get(escola=escola, data=data)
        eh_dia_letivo = dia_calendario.dia_letivo
    except DiaCalendario.DoesNotExist:
        eh_dia_letivo = True
    eh_dia_de_suspensao = DiaSuspensaoAtividades.eh_dia_de_suspensao(escola, data)
    periodos_escolares_alteracao = alteracao.substituicoes.values_list('periodo_escolar')
    return ((not eh_dia_letivo or eh_dia_de_suspensao) and
            not escola.grupos_inclusoes.filter(
                inclusoes_normais__cancelado=False,
                inclusoes_normais__data=data,
                quantidades_por_periodo__periodo_escolar__in=periodos_escolares_alteracao,
                status='CODAE_AUTORIZADO').exists() and
            not escola.inclusoes_continuas.filter(
                status='CODAE_AUTORIZADO',
                data_inicial__lte=data,
                data_final__gte=data,
                quantidades_por_periodo__periodo_escolar__in=periodos_escolares_alteracao,
                quantidades_por_periodo__cancelado=False).filter(
                    Q(quantidades_por_periodo__dias_semana__icontains=DiaCalendario.SABADO) |
                    Q(quantidades_por_periodo__dias_semana__icontains=DiaCalendario.DOMINGO)).exists())
