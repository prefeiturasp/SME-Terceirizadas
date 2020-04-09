import math

from ..dados_comuns.models import LogSolicitacoesUsuario


def formata_logs(logs):
    if logs.filter(status_evento__in=[
        LogSolicitacoesUsuario.CODAE_AUTORIZOU,
        LogSolicitacoesUsuario.CODAE_NEGOU]
    ).exists():
        logs = logs.exclude(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU)
    return logs.exclude(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO)


def get_width(fluxo, logs):
    fluxo_utilizado = formata_logs(logs) if len(logs) > len(formata_logs(logs)) else fluxo
    return str(math.floor(99 / len(fluxo_utilizado))) + '%'
