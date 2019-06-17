import uuid

from django.db import models


class Lote(models.Model):
    """Lote de escolas"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField("Nome", max_length=160)
    dre = models.ForeignKey('escola.DiretoriaRegional', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome


class Terceirizada(models.Model):
    """Empresa Terceirizada"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField("Nome", max_length=160)
    lote = models.ManyToManyField(Lote, blank=True)

    def __str__(self):
        return self.nome
