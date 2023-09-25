from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.dados_comuns.constants import (
    COORDENADOR_CODAE_DILOG_LOGISTICA,
    DILOG_CRONOGRAMA,
    DILOG_DIRETORIA,
    DINUTRE_DIRETORIA
)


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
                'CRONOGRAMA_CIENTE',
                'APROVADO_DINUTRE',
                'REPROVADO_DINUTRE'
            ],
            DILOG_DIRETORIA: [
                'APROVADO_DINUTRE',
                'REPROVADO_DINUTRE',
                'APROVADO_DILOG',
                'REPROVADO_DILOG'
            ],
            DILOG_CRONOGRAMA: [
                'EM_ANALISE',
                'APROVADO_DILOG',
                'REPROVADO_DILOG'
            ],
            COORDENADOR_CODAE_DILOG_LOGISTICA: [
                'EM_ANALISE',
                'APROVADO_DILOG',
                'REPROVADO_DILOG'
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
