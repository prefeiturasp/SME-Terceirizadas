from django.apps import AppConfig
from django.db.models.signals import post_save


class CardapioConfig(AppConfig):
    name = 'sme_terceirizadas.cardapio'

    def ready(self):
        from .models import InversaoCardapio, AlteracaoCardapio, GrupoSuspensaoAlimentacao
        from .signals import salva_rastro_inversao_alteracao_suspensao

        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=AlteracaoCardapio)
        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=InversaoCardapio)
        post_save.connect(salva_rastro_inversao_alteracao_suspensao, sender=GrupoSuspensaoAlimentacao)
