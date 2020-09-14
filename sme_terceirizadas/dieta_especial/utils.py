from datetime import date

from rest_framework.pagination import PageNumberPagination

from ..dados_comuns.fluxo_status import DietaEspecialWorkflow
from .models import SolicitacaoDietaEspecial


def dietas_especiais_a_terminar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_termino__lt=date.today(),
        ativo=True,
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def termina_dietas_especiais(usuario):
    for solicitacao in dietas_especiais_a_terminar():
        solicitacao.termina(usuario)


class RelatorioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
