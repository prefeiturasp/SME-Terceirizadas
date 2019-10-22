from django.apps import AppConfig
from django.db.models.signals import post_save


class KitLancheConfig(AppConfig):
    name = 'sme_terceirizadas.kit_lanche'

    def ready(self):
        from .models import SolicitacaoKitLancheAvulsa
        from ..dados_comuns.signals import salva_rastro_inversao_alteracao_suspensao

        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=SolicitacaoKitLancheAvulsa)
