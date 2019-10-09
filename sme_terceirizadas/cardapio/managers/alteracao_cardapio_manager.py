import datetime

from django.db import models

from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow


class AlteracoesCardapioDestaSemanaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(days=7)
        return super(AlteracoesCardapioDestaSemanaManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class AlteracoesCardapioDesteMesManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(days=31)
        return super(AlteracoesCardapioDesteMesManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class AlteracoesCardapioVencidaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        return super(AlteracoesCardapioVencidaManager, self).get_queryset(
        ).filter(
            data_inicial__lt=hoje
        ).filter(
            status__in=[PedidoAPartirDaEscolaWorkflow.RASCUNHO,
                        PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
                        PedidoAPartirDaEscolaWorkflow.DRE_PEDIU_ESCOLA_REVISAR]
        )
