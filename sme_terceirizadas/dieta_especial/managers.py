from django.db import models


class AlimentoProprioManager(models.Manager):

    def get_queryset(self):
        return super(AlimentoProprioManager, self).get_queryset().filter(tipo='P')
