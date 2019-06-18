import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Descritivel(models.Model):
    nome = models.CharField(_("Nome"), blank=True, null=True, max_length=50)
    descricao = models.TextField(_("Descricao"), blank=True, null=True, max_length=256)

    class Meta:
        abstract = True


class Motivos(models.Model):
    motivo = models.TextField("Motivo", blank=True, null=True, max_length=256)

    class Meta:
        abstract = True


class Ativavel(models.Model):
    ativo = models.BooleanField(_("Está Ativo"), default=True)

    class Meta:
        abstract = True


class RegistroHora(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class IntervaloDeTempo(models.Model):
    data_hora_inicial = models.DateTimeField(auto_now_add=True)
    data_hora_final = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class IntervaloDeDia(models.Model):
    data_inicial = models.DateField()
    data_final = models.DateField()

    class Meta:
        abstract = True


class TemChaveExterna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
