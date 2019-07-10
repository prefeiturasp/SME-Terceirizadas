import datetime

from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje
from sme_pratoaberto_terceirizadas.alimento.models import TipoRefeicao
from sme_pratoaberto_terceirizadas.inclusao_alimentacao import models


def validar_formato_data(data_texto, lista_erros):
    try:
        return datetime.datetime.strptime(data_texto, '%d/%m/%Y')
    except ValueError:
        lista_erros.append(_('Formato de data incorreto, deve ser DD/MM/AAAA'))


def validar_dias_da_semana(dias_semana, lista_erros):
    try:
        for dia_semana in dias_semana:
            if dia_semana not in ['0', '1', '2', '3', '4', '5', '6', ',']:
                return lista_erros.append(_('dias da semana invalido'))
    except ValueError:
        lista_erros.append(_('dias da semana invalido'))


def objeto_existe(query_set, **kwargs):
    return query_set.objects.filter(**kwargs).exists()


def obter_objeto(query_set, **kwargs):
    return query_set.objects.get(**kwargs)


def _checar_dados_requeridos(request_data):
    dados_requeridos = ['motivos_dia']
    return all(elem in request_data for elem in dados_requeridos)


def checar_dados_genericos_requeridos(request_data, dados_requeridos):
    return all(elem in request_data for elem in dados_requeridos)


def _validar_motivo(request_data, erros):
    motivo = request_data.get('motivo')
    motivo_existe = objeto_existe(models.MotivoInclusaoAlimentacao, nome=motivo)
    if not motivo_existe:
        erros.append(_('Motivo não existe'))


def _validar_status(request_data, erros):
    status = request_data.get('status')
    status_existe = objeto_existe(models.InclusaoAlimentacaoStatus, nome=status)
    if 'status' in request_data and not status_existe:
        erros.append("Status não existe")


def obter_lista_erros(request_data):
    erros = list()

    if not _checar_dados_requeridos(request_data):
        return ['Parâmetros faltando']

    if not _carga_dados_eh_valida(request_data):
        return ['Formato de requisição inválido']

    _validar_descricoes(request_data, erros)
    _validar_status(request_data, erros)
    _validar_bloco_data(request_data, erros)
    return erros


def _carga_dados_eh_valida(request_data):
    return request_data and isinstance(request_data, dict)


def _validar_bloco_data(request_data, erros):
    motivos_dia = request_data.get('motivos_dia')
    for motivo_dia in motivos_dia:
        _validar_motivo(motivo_dia, erros)
        if motivo_dia.get('data', None):
            _data_hora = validar_formato_data(motivo_dia.get('data'), erros)
            if _data_hora and _data_hora.date() < obter_dias_uteis_apos_hoje(2):
                erros.append('Mínimo de 2 dias úteis para fazer o pedido')
        else:
            validar_formato_data(motivo_dia.get('do_dia'), erros)
            validar_formato_data(motivo_dia.get('ate_dia'), erros)
            if 'dias_semana' in request_data:
                validar_dias_da_semana(motivo_dia.get('dias_semana'), erros)


def _validar_descricao(descricao, erros):
    tipos_refeicoes = descricao.get('select') if isinstance(descricao.get('select'), list) else [
        descricao.get('select')]
    #print(tipos_refeicoes)
    numero_de_estudantes = descricao.get('numero')
    for tipo_refeicao in tipos_refeicoes:
        if not objeto_existe(TipoRefeicao, nome=tipo_refeicao):
            erros.append('Tipo de refeição não existe')
    if not numero_de_estudantes.isdigit():
        erros.append('Número de estudantes precisa vir como inteiro')


def _validar_descricoes(request_data, erros):
    descricao_primeiro_periodo = request_data.get('descricao_primeiro_periodo', None)
    descricao_segundo_periodo = request_data.get('descricao_segundo_periodo', None)
    descricao_terceiro_periodo = request_data.get('descricao_terceiro_periodo', None)
    descricao_quarto_periodo = request_data.get('descricao_quarto_periodo', None)
    descricao_integral = request_data.get('descricao_integral', None)
    if not (descricao_primeiro_periodo or descricao_segundo_periodo or descricao_terceiro_periodo
            or descricao_quarto_periodo or descricao_integral):
        erros.append("Obrigatório ao menos um período")
    if descricao_primeiro_periodo:
        _validar_descricao(descricao_primeiro_periodo, erros)
    if descricao_segundo_periodo:
        _validar_descricao(descricao_segundo_periodo, erros)
    if descricao_terceiro_periodo:
        _validar_descricao(descricao_terceiro_periodo, erros)
    if descricao_quarto_periodo:
        _validar_descricao(descricao_quarto_periodo, erros)
    if descricao_integral:
        _validar_descricao(descricao_integral, erros)
