import datetime

from django.db import models


class AlteracoesCardapioPrazoVencendoManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.datetime.today() + datetime.timedelta(days=2)
        return super(AlteracoesCardapioPrazoVencendoManager, self).get_queryset().filter(data_inicial__lte=data_limite)


class AlteracoesCardapioPrazoLimiteManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = datetime.datetime.today() + datetime.timedelta(days=3)
        data_limite_final = datetime.datetime.today() + datetime.timedelta(days=4)

        return super(AlteracoesCardapioPrazoLimiteManager, self)\
            .get_queryset().filter(data_inicial__range=(data_limite_inicial, data_limite_final))


class AlteracoesCardapioPrazoRegularManager(models.Manager):
    def get_queryset(self):
        data_limite = datetime.datetime.today() + datetime.timedelta(days=5)
        return super(AlteracoesCardapioPrazoRegularManager, self).get_queryset().filter(data_inicial__gt=data_limite)
