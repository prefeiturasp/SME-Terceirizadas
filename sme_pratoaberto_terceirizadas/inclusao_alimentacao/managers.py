import datetime
from django.db import models

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje


class InclusoesDeAlimentacaoContinuaPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        return super(InclusoesDeAlimentacaoContinuaPrazoVencendoManager, self).get_queryset().filter(
            data_inicial__range=(datetime.date.today(), data_limite)
        )


class InclusoesDeAlimentacaoContinuaPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.date.today()
        print(data_limite)
        return super(InclusoesDeAlimentacaoContinuaPrazoVencendoHojeManager, self).get_queryset().filter(
            data_inicial=data_limite
        )


class InclusoesDeAlimentacaoContinuaPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(InclusoesDeAlimentacaoContinuaPrazoLimiteManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoContinuaPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(InclusoesDeAlimentacaoContinuaPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoContinuaPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(InclusoesDeAlimentacaoContinuaPrazoRegularManager, self).get_queryset().filter(
            data_inicial__gte=data_limite
        )


class InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA7DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=31)
        return super(InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA30DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class InclusoesDeAlimentacaoNormalPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        return super(InclusoesDeAlimentacaoNormalPrazoVencendoManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(datetime.date.today(), data_limite)
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.date.today()
        print(data_limite)
        return super(InclusoesDeAlimentacaoNormalPrazoVencendoHojeManager, self).get_queryset().filter(
            inclusoes_normais__data=data_limite
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(InclusoesDeAlimentacaoNormalPrazoLimiteManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(InclusoesDeAlimentacaoNormalPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(InclusoesDeAlimentacaoNormalPrazoRegularManager, self).get_queryset().filter(
            inclusoes_normais__data__gte=data_limite
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoRegularDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(InclusoesDeAlimentacaoNormalPrazoRegularDaquiA7DiasManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        ).distinct()


class InclusoesDeAlimentacaoNormalPrazoRegularDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=31)
        return super(InclusoesDeAlimentacaoNormalPrazoRegularDaquiA30DiasManager, self).get_queryset().filter(
            inclusoes_normais__data__range=(data_limite_inicial, data_limite_final)
        ).distinct()
