from django.db import models
from ..dados_comuns.behaviors import CriadoEm, TemChaveExterna

class Classificacao(TemChaveExterna, CriadoEm):
    tipo = models.CharField('tipo', max_length=2, blank=True)
    descricao = models.CharField('descricao', max_length=250, blank=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'Classificação'