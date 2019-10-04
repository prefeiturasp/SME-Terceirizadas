import datetime

from django.db import models
from django.db.models import Q

from ..dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow


class InclusoesDeAlimentacaoContinuaDestaSemanaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(days=7)
        return super(InclusoesDeAlimentacaoContinuaDestaSemanaManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoContinuaDesteMesManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(days=31)
        return super(InclusoesDeAlimentacaoContinuaDesteMesManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoContinuaVencidaDiasManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(InclusoesDeAlimentacaoContinuaVencidaDiasManager, self).get_queryset(
        ).filter(
            data_inicial__lt=hoje
        ).filter(status__in=[
            PedidoAPartirDaEscolaWorkflow.RASCUNHO,
            PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
            PedidoAPartirDaEscolaWorkflow.DRE_PEDIU_ESCOLA_REVISAR,
            PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
        ])


class GrupoInclusoesDeAlimentacaoNormalDestaSemanaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(days=7)
        return super(GrupoInclusoesDeAlimentacaoNormalDestaSemanaManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        )


class GrupoInclusoesDeAlimentacaoNormalDesteMesManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = datetime.date.today() + datetime.timedelta(days=31)
        return super(GrupoInclusoesDeAlimentacaoNormalDesteMesManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        )


class GrupoInclusoesDeAlimentacaoNormalVencidosDiasManager(models.Manager):
    # TODO: se alguma tiver vencida cancela o grupo todo, ou espera todas as inclusoes_normais
    # vencerem para dar como vencido o grupo? verificar...
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(GrupoInclusoesDeAlimentacaoNormalVencidosDiasManager, self).get_queryset(
        ).filter(
            inclusoes_normais__data__lt=hoje
        ).filter(
            ~Q(status__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
                           PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
                           PedidoAPartirDaEscolaWorkflow.CANCELADO_AUTOMATICAMENTE])
        )
