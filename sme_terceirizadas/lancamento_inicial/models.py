from django.db import models

from sme_terceirizadas.dados_comuns.behaviors import (  # noqa I101
    CriadoEm,
    CriadoPor,
    Logs,
    TemChaveExterna,
    TemData,
)

class LancamentoDiario(CriadoEm, CriadoPor, TemData,
                       Logs, TemChaveExterna, models.Model):
    escola_periodo_escolar = models.ForeignKey(
        'escola.EscolaPeriodoEscolar',
        on_delete=models.DO_NOTHING
    )
    tipo_dieta = models.ForeignKey(
        'dieta_especial.ClassificacaoDieta',
        on_delete=models.DO_NOTHING
    )
    frequencia = models.IntegerField(null=True)
    lanche_4h = models.IntegerField(null=True)
    lanche_5h = models.IntegerField(null=True)
    observacoes = models.TextField(blank=True)


class Refeicao(models.Model):
    ref_oferta = models.IntegerField(null=True)
    ref_repet = models.IntegerField(null=True)
    sob_oferta = models.IntegerField(null=True)
    sob_repet = models.IntegerField(null=True)
    lancamento = models.ForeignKey(
        LancamentoDiario,
        on_delete=models.CASCADE,
        related_name="refeicoes"
    )
