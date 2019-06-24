import uuid

from django.db import models

from sme_pratoaberto_terceirizadas.abstract_shareable import TemChaveExterna, Descritivel, Nomeavel


class Lote(TemChaveExterna, Nomeavel):
    """Lote de escolas"""
    diretoria_regional = models.ForeignKey('escola.DiretoriaRegional',
                                           on_delete=models.DO_NOTHING,
                                           null=True,
                                           blank=True)

    def __str__(self):
        return self.nome


class Terceirizada(models.Model):
    """Empresa Terceirizada"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField("Nome", max_length=160)
    lote = models.ManyToManyField(Lote, blank=True)

    def __str__(self):
        return self.nome
