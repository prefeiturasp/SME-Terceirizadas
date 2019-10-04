import datetime

from django.db import models
from django.db.models import Q

from sme_terceirizadas.dados_comuns.constants import DIAS_UTEIS_LIMITE_INFERIOR
from ...dados_comuns.constants import DIAS_UTEIS_LIMITE_SUPERIOR, MINIMO_DIAS_PARA_PEDIDO
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow


class InversaoCardapioPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        return super(InversaoCardapioPrazoVencendoManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__lte=MINIMO_DIAS_PARA_PEDIDO) | Q(cardapio_para__data__lte=MINIMO_DIAS_PARA_PEDIDO)
        )


class InversaoCardapioPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(InversaoCardapioPrazoVencendoHojeManager, self).get_queryset().filter(
            Q(cardapio_de__data=hoje) | Q(cardapio_para__data=hoje)
        )


class InversaoCardapioPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.date.today()
        data_limite_final = datetime.date.today() + datetime.timedelta(days=7)
        return super(InversaoCardapioPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            Q(cardapio_de__data__range=(data_limite_inicial, data_limite_final)) |  # noqa W504
            Q(cardapio_para__data__range=(data_limite_inicial, data_limite_final))
        ).filter(cardapio_de__data__gte=data_limite_inicial, cardapio_para__data__gte=data_limite_inicial)


class InversaoCardapioPrazoLimiteDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.date.today()
        data_limite_final = datetime.date.today() + datetime.timedelta(days=30)
        return super(InversaoCardapioPrazoLimiteDaquiA30DiasManager, self).get_queryset().filter(
            Q(cardapio_de__data__range=(data_limite_inicial, data_limite_final)) |  # noqa W504
            Q(cardapio_para__data__range=(data_limite_inicial, data_limite_final))
        ).filter(cardapio_de__data__gte=data_limite_inicial, cardapio_para__data__gte=data_limite_inicial)


class InversaoCardapioPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        return super(InversaoCardapioPrazoLimiteManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__range=(DIAS_UTEIS_LIMITE_INFERIOR, DIAS_UTEIS_LIMITE_SUPERIOR)) |  # noqa W504
            Q(cardapio_para__data__range=(DIAS_UTEIS_LIMITE_INFERIOR, DIAS_UTEIS_LIMITE_SUPERIOR))
        )


class InversaoCardapioVencidaManager(models.Manager):
    # TODO verificar melhor a regra de vencimento de cardapio.
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(InversaoCardapioVencidaManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__lt=hoje) | Q(cardapio_para__data__lt=hoje)
        ).filter(
            ~Q(status__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
                           PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
                           PedidoAPartirDaEscolaWorkflow.CANCELADO_AUTOMATICAMENTE])
        ).distinct()
