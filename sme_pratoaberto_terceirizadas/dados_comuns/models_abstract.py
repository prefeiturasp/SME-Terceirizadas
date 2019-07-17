import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils import Choices


class Iniciais(models.Model):
    iniciais = models.CharField("Iniciais", blank=True, null=True, max_length=10)

    class Meta:
        abstract = True


class Descritivel(models.Model):
    descricao = models.TextField("Descricao", blank=True, null=True)

    class Meta:
        abstract = True


class Nomeavel(models.Model):
    nome = models.CharField("Nome", blank=True, null=True, max_length=50)

    class Meta:
        abstract = True


class Motivo(models.Model):
    motivo = models.TextField("Motivo", blank=True, null=True)

    class Meta:
        abstract = True


class Ativavel(models.Model):
    ativo = models.BooleanField("Está ativo?", default=True)

    class Meta:
        abstract = True


class CriadoEm(models.Model):
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)

    class Meta:
        abstract = True


class IntervaloDeTempo(models.Model):
    data_hora_inicial = models.DateTimeField("Data/hora inicial")
    data_hora_final = models.DateTimeField("Data/hora final")

    class Meta:
        abstract = True


class IntervaloDeDia(models.Model):
    data_inicial = models.DateField("Data inicial")
    data_final = models.DateField("Data final")

    class Meta:
        abstract = True


class TemData(models.Model):
    data = models.DateField("Data")

    class Meta:
        abstract = True


class TemChaveExterna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class StatusValidacao(models.Model):
    """
     - https://steelkiwi.com/blog/best-practices-working-django-models-python/
     - https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63
    """
    STATUSES = Choices(
        (0, 'DRE_A_VALIDAR', 'A validar pela DRE'),
        (1, 'DRE_APROVADO', 'Aprovado pela DRE'),
        (2, 'DRE_REPROVADO', 'Reprovado pela DRE'),
        (3, 'CODAE_A_VALIDAR', 'A validar pela CODAE'),  # QUANDO A DRE VALIDA
        (4, 'CODAE_APROVADO', 'Aprovado pela CODAE'),  # CODAE RECEBE
        (5, 'CODAE_REPROVADO', 'Reprovado pela CODAE'),
        (6, 'TERCEIRIZADA_A_VISUALIZAR', 'Terceirizada a visualizar'),
        (7, 'TERCEIRIZADA_A_VISUALIZADO', 'Terceirizada visualizado')  # TOMOU CIENCIA, TODOS DEVEM FICAR SABENDO...
    )
    status = models.IntegerField(choices=STATUSES, default=STATUSES.DRE_A_VALIDAR)

    class Meta:
        abstract = True


class DiasSemana(models.Model):
    SEGUNDA = 1
    TERCA = 2
    QUARTA = 3
    QUINTA = 4
    SEXTA = 5
    SABADO = 6
    DOMINGO = 7

    DIAS = (
        (SEGUNDA, 'Segunda'),
        (TERCA, 'Terça'),
        (QUINTA, 'Quarta'),
        (QUARTA, 'Quinta'),
        (SEXTA, 'Sexta'),
        (SABADO, 'Sábado'),
        (DOMINGO, 'Domingo'),
    )

    dias_semana = ArrayField(models.PositiveSmallIntegerField(choices=DIAS,
                                                              default=[],
                                                              null=True, blank=True))

    def dias_semana_display(self):
        result = ''
        choices = dict(self.DIAS)
        for index, value in enumerate(self.dias_semana):
            result += "{0}".format(choices[value])
            if not index == len(self.dias_semana) - 1:
                result += ', '
        return result

    class Meta:
        abstract = True
