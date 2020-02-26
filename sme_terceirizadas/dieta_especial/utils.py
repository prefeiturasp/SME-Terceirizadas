from datetime import date

from ..dados_comuns.fluxo_status import DietaEspecialWorkflow
from .models import SolicitacaoDietaEspecial


def dietas_especiais_a_expirar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_expiracao__lt=date.today(),
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def expira_dietas_especiais():
    for solicitacao in dietas_especiais_a_expirar():
        solicitacao.expira()
