from django.db import models

from ..dados_comuns.models_abstract import (Ativavel, Descritivel, CriadoEm, Ativavel,
                                            Nomeavel, IntervaloDeDia, TemData)
from ..escola.models import PeriodoEscolar
from ..perfil.models import Usuario


class QuantidadePorPeriodo(models.Model):
    numero_alunos = models.PositiveSmallIntegerField()
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao')


class MotivoInclusaoContinua(Nomeavel):
    """
        continuo -  mais educacao
        continuo-sp integral
        continuo - outro
    """


class InclusaoAlimentacaoContinua(IntervaloDeDia, Descritivel):
    outro_motivo = models.CharField("Outro motivo", blank=True, null=True, max_length=50)
    motivo = models.ForeignKey(MotivoInclusaoContinua, on_delete=models.DO_NOTHING)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    quantidades_periodo = models.ManyToManyField(QuantidadePorPeriodo)
    # TODO: status aqui.


class MotivoInclusaoNormal(Nomeavel):
    """
        reposicao de aula
        dia de familia
        outro
    """


class InclusaoAlimentacaoNormal(TemData):
    quantidades_periodo = models.ManyToManyField(QuantidadePorPeriodo)
    prioritario = models.BooleanField(default=False)
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField("Outro motivo", blank=True, null=True, max_length=50)


class GrupoInclusaoAlimentacaoNormal(Descritivel):
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    # TODO: status aqui.
