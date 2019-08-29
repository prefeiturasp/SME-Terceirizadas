import datetime

from django.db import models
from django.db.models import Q

from ...dados_comuns.constants import MINIMO_DIAS_PARA_PEDIDO, QUANTIDADE_DIAS_OK_PARA_PEDIDO
from ...dados_comuns.fluxo_status import PedidoAPartirDaDiretoriaRegionalWorkflow
from ...dados_comuns.utils import obter_dias_uteis_apos_hoje


class SolicitacaoUnificadaPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=MINIMO_DIAS_PARA_PEDIDO)
        return super(SolicitacaoUnificadaPrazoVencendoManager, self).get_queryset(
        ).filter(
            solicitacao_kit_lanche__data__lte=data_limite
        )


class SolicitacaoUnificadaPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(SolicitacaoUnificadaPrazoVencendoHojeManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data=hoje
        )


class SolicitacaoUnificadaPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.date.today()
        data_limite_final = datetime.date.today() + datetime.timedelta(days=7)
        return super(SolicitacaoUnificadaPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoUnificadaPrazoLimiteDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.date.today()
        data_limite_final = datetime.date.today() + datetime.timedelta(days=30)
        return super(SolicitacaoUnificadaPrazoLimiteDaquiA30DiasManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoUnificadaPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=MINIMO_DIAS_PARA_PEDIDO + 1)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=QUANTIDADE_DIAS_OK_PARA_PEDIDO)
        return super(SolicitacaoUnificadaPrazoLimiteManager, self).get_queryset(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoUnificadaVencidaManager(models.Manager):
    # TODO verificar melhor a regra de vencimento de cardapio.
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(SolicitacaoUnificadaVencidaManager, self).get_queryset(
        ).filter(
            solicitacao_kit_lanche__data__lt=hoje
        ).filter(
            ~Q(status__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.TERCEIRIZADA_TOMA_CIENCIA,
                           PedidoAPartirDaDiretoriaRegionalWorkflow.CANCELAMENTO_AUTOMATICO])
        ).distinct()
