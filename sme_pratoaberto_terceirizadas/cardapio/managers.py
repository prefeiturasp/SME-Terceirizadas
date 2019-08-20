import datetime

from django.db import models
from django.db.models import Q

from sme_pratoaberto_terceirizadas.dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje


class AlteracoesCardapioPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=2)
        return super(AlteracoesCardapioPrazoVencendoManager, self).get_queryset().filter(data_inicial__lte=data_limite)


class AlteracoesCardapioPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5)

        return super(AlteracoesCardapioPrazoLimiteManager, self) \
            .get_queryset().filter(data_inicial__range=(data_limite_inicial, data_limite_final))


class AlteracoesCardapioPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(AlteracoesCardapioPrazoRegularManager, self).get_queryset().filter(data_inicial__gte=data_limite)


class AlteracoesCardapioVencidaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(AlteracoesCardapioVencidaManager, self).get_queryset(
        ).filter(
            data_inicial__lt=hoje
        ).filter(
            ~Q(status__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMA_CIENCIA,
                           PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELA_48H_ANTES,
                           PedidoAPartirDaEscolaWorkflow.CANCELAMENTO_AUTOMATICO]
               )
        )


class InversaoCardapioVencidaManager(models.Manager):
    # TODO verificar melhor a regra de vencimento de cardapio.
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(InversaoCardapioVencidaManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__lt=hoje) | Q(cardapio_para__data__lt=hoje)
        ).filter(
            ~Q(status__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMA_CIENCIA,
                           PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELA_48H_ANTES,
                           PedidoAPartirDaEscolaWorkflow.CANCELAMENTO_AUTOMATICO])
        ).distinct()
