import datetime

from django.db import models
from django.db.models import Q

from ...dados_comuns.constants import MINIMO_DIAS_PARA_PEDIDO, QUANTIDADE_DIAS_OK_PARA_PEDIDO
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.utils import obter_dias_uteis_apos_hoje


class InversaoCardapioPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=MINIMO_DIAS_PARA_PEDIDO)
        return super(InversaoCardapioPrazoVencendoManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__lte=data_limite) | Q(cardapio_para__data__lte=data_limite)
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
            Q(cardapio_de__data__range=(data_limite_inicial, data_limite_final))
            |
            Q(cardapio_para__data__range=(data_limite_inicial, data_limite_final))
        ).filter(cardapio_de__data__gt=data_limite_inicial)


class InversaoCardapioPrazoLimiteDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.date.today()
        data_limite_final = datetime.date.today() + datetime.timedelta(days=30)
        return super(InversaoCardapioPrazoLimiteDaquiA30DiasManager, self).get_queryset().filter(
            Q(cardapio_de__data__range=(data_limite_inicial, data_limite_final))
            |
            Q(cardapio_para__data__range=(data_limite_inicial, data_limite_final))
        ).filter(cardapio_de__data__gt=data_limite_inicial)


class InversaoCardapioPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=MINIMO_DIAS_PARA_PEDIDO + 1)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=QUANTIDADE_DIAS_OK_PARA_PEDIDO)

        return super(InversaoCardapioPrazoLimiteManager, self).get_queryset(
        ).filter(
            Q(cardapio_de__data__range=(data_limite_inicial, data_limite_final))
            |
            Q(cardapio_para__data__range=(data_limite_inicial, data_limite_final))
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
