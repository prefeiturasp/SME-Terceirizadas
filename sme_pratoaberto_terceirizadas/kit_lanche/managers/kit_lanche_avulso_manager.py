import datetime

from django.db import models
from django.db.models import Q

from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.utils import obter_dias_uteis_apos_hoje


class SolicitacaoKitLancheAvulsaPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=2)
        return super(SolicitacaoKitLancheAvulsaPrazoVencendoManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(datetime.date.today(), data_limite)
        )


class SolicitacaoKitLancheAvulsaPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.date.today()
        return super(SolicitacaoKitLancheAvulsaPrazoVencendoHojeManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data=data_limite
        )


class SolicitacaoKitLancheAvulsaPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5) - datetime.timedelta(days=1)
        return super(SolicitacaoKitLancheAvulsaPrazoLimiteManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoKitLancheAvulsaPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(SolicitacaoKitLancheAvulsaPrazoRegularManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__gte=data_limite
        )


class SolicitacaoKitLancheAvulsaPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5) - datetime.timedelta(days=1)
        return super(SolicitacaoKitLancheAvulsaPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoKitLancheAvulsaPrazoRegularDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(SolicitacaoKitLancheAvulsaPrazoRegularDaquiA7DiasManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoKitLancheAvulsaPrazoRegularDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=2)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=31)
        return super(SolicitacaoKitLancheAvulsaPrazoRegularDaquiA30DiasManager, self).get_queryset().filter(
            solicitacao_kit_lanche__data__range=(data_limite_inicial, data_limite_final)
        )


class SolicitacaoKitLancheAvulsaVencidaDiasManager(models.Manager):
    """
    retorna todos os pedidos que ja tenham passado da data e que o fluxo não tenha terminado
    """

    def get_queryset(self):
        hoje = datetime.date.today()
        return super(SolicitacaoKitLancheAvulsaVencidaDiasManager, self).get_queryset(
        ).filter(
            solicitacao_kit_lanche__data__lt=hoje
        ).filter(
            ~Q(solicitacao_kit_lanche__data__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMA_CIENCIA,
                                                 PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELA_48H_ANTES,
                                                 PedidoAPartirDaEscolaWorkflow.CANCELAMENTO_AUTOMATICO])
        )
