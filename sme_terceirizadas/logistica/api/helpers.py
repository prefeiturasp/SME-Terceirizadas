from unicodedata import normalize

from django.db.models import Case, Value, When
from django.db.models.fields import CharField
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow
from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.logistica.models import Guia


def remove_acentos_de_strings(nome: str) -> str:
    return normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')


def retorna_status_das_requisicoes(status_list: list) -> list:  # noqa C901
    lista_com_status = []
    todos_status = [SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO,
                    SolicitacaoRemessaWorkFlow.DILOG_ENVIA,
                    SolicitacaoRemessaWorkFlow.PAPA_CANCELA,
                    SolicitacaoRemessaWorkFlow.DISTRIBUIDOR_CONFIRMA,
                    SolicitacaoRemessaWorkFlow.DISTRIBUIDOR_SOLICITA_ALTERACAO]
    if len(status_list) == 0:
        return todos_status
    elif len(status_list) == 1:
        if status_list[0] == ' ' or status_list[0] == '':
            return todos_status
    for status in status_list:
        if status == 'Todos':
            return todos_status
        elif status == 'Aguardando envio':
            lista_com_status.append(
                SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO
            )
        elif status == 'Enviada':
            lista_com_status.append(
                SolicitacaoRemessaWorkFlow.DILOG_ENVIA
            )
        elif status == 'Cancelada':
            lista_com_status.append(
                SolicitacaoRemessaWorkFlow.PAPA_CANCELA
            )
        elif status == 'Confirmada':
            lista_com_status.append(
                SolicitacaoRemessaWorkFlow.DISTRIBUIDOR_CONFIRMA
            )
        elif status == 'Em análise':
            lista_com_status.append(
                SolicitacaoRemessaWorkFlow.DISTRIBUIDOR_SOLICITA_ALTERACAO
            )
    return lista_com_status


def retorna_status_para_usuario(status_evento: str) -> str:  # noqa C901
    if status_evento == 'Papa enviou a requisição':
        return 'Aguardando envio'
    elif status_evento == 'Dilog Enviou a requisição':
        return 'Enviada'
    elif status_evento == 'Distribuidor confirmou requisição':
        return 'Confirmada'
    elif status_evento == 'Distribuidor pede alteração da requisição':
        return 'Em análise'
    else:
        return 'Cancelada'


def retorna_dados_normalizados_excel_visao_distribuidor(queryset):
    requisicoes = queryset.annotate(status_requisicao=Case(
        When(status='AGUARDANDO_ENVIO', then=Value('Aguardando envio')),
        When(status='DILOG_ENVIA', then=Value('Recebida')),
        When(status='CANCELADA', then=Value('Cancelada')),
        When(status='DISTRIBUIDOR_CONFIRMA', then=Value('Confirmada')),
        When(status='DISTRIBUIDOR_SOLICITA_ALTERACAO', then=Value('Em análise')),
        When(status='DILOG_ACEITA_ALTERACAO', then=Value('Alterada')),
        output_field=CharField(),
    )).values(
        'numero_solicitacao', 'status_requisicao', 'quantidade_total_guias', 'guias__numero_guia',
        'guias__data_entrega', 'guias__codigo_unidade', 'guias__nome_unidade', 'guias__endereco_unidade',
        'guias__endereco_unidade', 'guias__numero_unidade', 'guias__bairro_unidade', 'guias__cep_unidade',
        'guias__cidade_unidade', 'guias__estado_unidade', 'guias__contato_unidade', 'guias__telefone_unidade',
        'guias__alimentos__nome_alimento', 'guias__alimentos__codigo_suprimento', 'guias__alimentos__codigo_papa',
        'guias__alimentos__embalagens__tipo_embalagem', 'guias__alimentos__embalagens__descricao_embalagem',
        'guias__alimentos__embalagens__capacidade_embalagem', 'guias__alimentos__embalagens__unidade_medida',
        'guias__alimentos__embalagens__qtd_volume')

    return requisicoes


def retorna_dados_normalizados_excel_visao_dilog(queryset):
    requisicoes = queryset.annotate(status_requisicao=Case(
        When(status='AGUARDANDO_ENVIO', then=Value('Aguardando envio')),
        When(status='DILOG_ENVIA', then=Value('Enviada')),
        When(status='CANCELADA', then=Value('Cancelada')),
        When(status='DISTRIBUIDOR_CONFIRMA', then=Value('Confirmada')),
        When(status='DISTRIBUIDOR_SOLICITA_ALTERACAO', then=Value('Em análise')),
        When(status='DILOG_ACEITA_ALTERACAO', then=Value('Alterada')),
        output_field=CharField(),
    ), codigo_eol_unidade=Value('', output_field=CharField())).values(
        'distribuidor__nome_fantasia', 'numero_solicitacao', 'status_requisicao', 'quantidade_total_guias',
        'guias__numero_guia', 'guias__status', 'guias__data_entrega', 'guias__codigo_unidade', 'guias__nome_unidade',
        'guias__endereco_unidade', 'guias__endereco_unidade', 'guias__numero_unidade', 'guias__bairro_unidade',
        'guias__cep_unidade', 'guias__cidade_unidade', 'guias__estado_unidade', 'guias__contato_unidade',
        'guias__telefone_unidade', 'guias__alimentos__nome_alimento', 'guias__alimentos__codigo_suprimento',
        'guias__alimentos__codigo_papa', 'guias__alimentos__embalagens__tipo_embalagem', 'codigo_eol_unidade',
        'guias__alimentos__embalagens__descricao_embalagem', 'guias__alimentos__embalagens__capacidade_embalagem',
        'guias__alimentos__embalagens__unidade_medida', 'guias__alimentos__embalagens__qtd_volume')

    escolas = Escola.objects.all().values('codigo_eol', 'codigo_codae')

    for requisicao in requisicoes:
        for escola in escolas:
            if requisicao['guias__codigo_unidade'] == escola['codigo_codae']:
                requisicao['codigo_eol_unidade'] = escola.get('codigo_eol', '')

    return requisicoes


def inicia_fluxo_guias(requisicao, user):
    guias = Guia.objects.filter(solicitacao=requisicao)
    try:
        for guia in guias:
            guia.inicia_fluxo(user)
    except InvalidTransitionError as e:
        return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)
