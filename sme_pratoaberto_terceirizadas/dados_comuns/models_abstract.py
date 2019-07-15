import uuid

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
    """ https://steelkiwi.com/blog/best-practices-working-django-models-python/ """
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
