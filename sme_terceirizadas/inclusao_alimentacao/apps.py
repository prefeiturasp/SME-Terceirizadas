from django.apps import AppConfig
from django.db.models.signals import post_save


class InclusaoAlimentacaoConfig(AppConfig):
    name = 'sme_terceirizadas.inclusao_alimentacao'

    def ready(self):
        from .models import InclusaoAlimentacaoContinua, GrupoInclusaoAlimentacaoNormal
        from ..dados_comuns.signals import salva_rastro_inversao_alteracao_suspensao

        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=InclusaoAlimentacaoContinua)
        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=GrupoInclusaoAlimentacaoNormal)
