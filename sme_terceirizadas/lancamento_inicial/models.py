from django.db import models

from ..dados_comuns.behaviors import CriadoEm, CriadoPor, Logs, TemChaveExterna, TemData  # noqa I101


class LancamentoDiario(CriadoEm, CriadoPor, TemData,
                       Logs, TemChaveExterna, models.Model):
    escola_periodo_escolar = models.ForeignKey(
        'escola.EscolaPeriodoEscolar',
        on_delete=models.DO_NOTHING
    )
    tipo_dieta = models.ForeignKey(
        'dieta_especial.ClassificacaoDieta',
        on_delete=models.DO_NOTHING,
        null=True
    )
    frequencia = models.IntegerField(null=True)
    lanche_4h = models.IntegerField(null=True)
    lanche_5h = models.IntegerField(null=True)
    ref_enteral = models.IntegerField(null=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return str(self.uuid)


class Refeicao(models.Model):
    ref_oferta = models.IntegerField(null=True)
    ref_repet = models.IntegerField(null=True)
    sob_oferta = models.IntegerField(null=True)
    sob_repet = models.IntegerField(null=True)
    lancamento = models.ForeignKey(
        LancamentoDiario,
        on_delete=models.CASCADE,
        related_name='refeicoes'
    )

    def __str__(self):
        return f'{self.id} - Pertencente ao lançamento ${self.lancamento.uuid}'
