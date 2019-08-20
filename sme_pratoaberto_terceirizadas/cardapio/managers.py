import datetime

from django.db import models

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje


class AlteracoesCardapioPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=2)
        return super(AlteracoesCardapioPrazoVencendoManager, self).get_queryset().filter(data_inicial__lte=data_limite)


class AlteracoesCardapioPrazoVencendoHojeManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.date.today()
        return super(AlteracoesCardapioPrazoVencendoHojeManager, self).get_queryset().filter(
            data_inicial=data_limite
        )


class AlteracoesCardapioPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=5)

        return super(AlteracoesCardapioPrazoLimiteManager, self)\
            .get_queryset().filter(data_inicial__range=(data_limite_inicial, data_limite_final))


class AlteracoesCardapioPrazoLimiteDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=3)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(AlteracoesCardapioPrazoLimiteDaquiA7DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class AlteracoesCardapioPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        return super(AlteracoesCardapioPrazoRegularManager, self).get_queryset().filter(data_inicial__gte=data_limite)


class AlteracoesCardapioPrazoRegularDaquiA7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=8)
        return super(AlteracoesCardapioPrazoRegularDaquiA7DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )


class AlteracoesCardapioPrazoRegularDaquiA30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=5)
        data_limite_final = datetime.date.today() + datetime.timedelta(days=31)
        return super(AlteracoesCardapioPrazoRegularDaquiA30DiasManager, self).get_queryset().filter(
            data_inicial__range=(data_limite_inicial, data_limite_final)
        )
