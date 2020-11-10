from django.db import models

from ...dados_comuns.behaviors import ModeloBase
from .guia import Guia


class Alimento(ModeloBase):
    guia = models.ForeignKey(
        Guia, on_delete=models.CASCADE, blank=True, null=True, related_name='alimentos')
    codigo_suprimento = models.CharField('Código suprimento', blank=True, max_length=100)
    codigo_papa = models.CharField('Código papa', blank=True, max_length=10)
    nome_alimento = models.CharField('Nome do alimento/produto', blank=True, max_length=100)
    embalagem = models.CharField('Embalagem', blank=True, max_length=100)
    qtd_volume = models.PositiveSmallIntegerField('Quantidade/Volume', blank=True)

    class Meta:
        verbose_name = 'Alimento'
        verbose_name_plural = 'Alimentos'
