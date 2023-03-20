
from sme_terceirizadas.dados_comuns.constants import DINUTRE_DIRETORIA


class DashboardSolicitacaoAlteracaoCronogramaProfiles:

    @staticmethod
    def get_dashboard_status(perfil: str) -> list:
        status = {
            DINUTRE_DIRETORIA: [
                'EM_ANALISE',
            ]
        }
        if perfil not in status:
            raise ValueError('Perfil não existe')

        return status[perfil]
