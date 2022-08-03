from django.db import models


from sme_terceirizadas.dados_comuns.behaviors import TemData, TemChaveExterna, CriadoEm, CriadoPor
from sme_terceirizadas.escola.models import TipoUnidadeEscolar


class DiaSobremesaDoce(TemData, TemChaveExterna, CriadoEm, CriadoPor):
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.data.strftime("%d/%m/%y")} - {self.tipo_unidade.iniciais}'

    class Meta:
        verbose_name = 'Dia de sobremesa doce'
        verbose_name_plural = 'Dias de sobremesa doce'
        ordering = ('data',)
