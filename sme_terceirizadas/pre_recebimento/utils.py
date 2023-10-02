from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.dados_comuns.constants import (
    COORDENADOR_CODAE_DILOG_LOGISTICA,
    DILOG_CRONOGRAMA,
    DILOG_DIRETORIA,
    DINUTRE_DIRETORIA
)
from sme_terceirizadas.dados_comuns.fluxo_status import CronogramaAlteracaoWorkflow as StatusAlteracao


class ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles:
    """
    Service para lidar com perfis de Dashboard para Solicitação de alteração de cronograma.

    Quando necessário, direcionar o perfil e a lista de status da solicitação que será retornada para
    o dashboard Exemplo NOVO_PERFIL : [status1, status2]
    """

    @staticmethod
    def get_dashboard_status(user) -> list:
        perfil = user.vinculo_atual.perfil.nome
        status = {
            DINUTRE_DIRETORIA: [
                StatusAlteracao.CRONOGRAMA_CIENTE,
                StatusAlteracao.APROVADO_DINUTRE,
                StatusAlteracao.REPROVADO_DINUTRE,
                StatusAlteracao.ALTERACAO_ENVIADA_FORNECEDOR,
                StatusAlteracao.FORNECEDOR_CIENTE
            ],
            DILOG_DIRETORIA: [
                StatusAlteracao.APROVADO_DINUTRE,
                StatusAlteracao.REPROVADO_DINUTRE,
                StatusAlteracao.APROVADO_DILOG,
                StatusAlteracao.REPROVADO_DILOG,
                StatusAlteracao.ALTERACAO_ENVIADA_FORNECEDOR,
                StatusAlteracao.FORNECEDOR_CIENTE
            ],
            DILOG_CRONOGRAMA: [
                StatusAlteracao.EM_ANALISE,
                StatusAlteracao.APROVADO_DILOG,
                StatusAlteracao.REPROVADO_DILOG,
                StatusAlteracao.ALTERACAO_ENVIADA_FORNECEDOR,
                StatusAlteracao.FORNECEDOR_CIENTE
            ],
            COORDENADOR_CODAE_DILOG_LOGISTICA: [
                StatusAlteracao.EM_ANALISE,
                StatusAlteracao.APROVADO_DILOG,
                StatusAlteracao.REPROVADO_DILOG,
                StatusAlteracao.ALTERACAO_ENVIADA_FORNECEDOR,
                StatusAlteracao.FORNECEDOR_CIENTE
            ],
        }

        if perfil not in status:
            raise ValueError('Perfil não existe')

        return status[perfil]


class UnidadeMedidaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LayoutDeEmbalagemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
