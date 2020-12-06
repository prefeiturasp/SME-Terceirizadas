from unicodedata import normalize

from sme_terceirizadas.dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow


def remove_acentos_de_strings(nome: str) -> str:
    return normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')


def retorna_status_das_requisicoes(status_list: list) -> list: # noqa C901
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


def retorna_status_para_usuario(status_evento: str) -> str: # noqa C901
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
