from django.core.validators import MinLengthValidator
from django.db import models

from ..dados_comuns.models_abstract import (
    TemChaveExterna, Nomeavel, Iniciais,
    Ativavel, Descritivel, IntervaloDeDia
)


class Edital(TemChaveExterna, Nomeavel, Descritivel, Ativavel, IntervaloDeDia):

    def __str__(self):
        return "{} válido de {} até {}".format(self.nome, self.data_inicial, self.data_final)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"


class Lote(TemChaveExterna, Nomeavel, Iniciais):
    """Lote de escolas"""
    diretoria_regional = models.ForeignKey('escola.DiretoriaRegional',
                                           on_delete=models.DO_NOTHING,
                                           related_name='lotes',
                                           null=True,
                                           blank=True)

    @property
    def escolas(self):
        return self.escolas

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"


class Terceirizada(TemChaveExterna, Ativavel):
    """Empresa Terceirizada"""

    nome_fantasia = models.CharField("Nome fantasia", max_length=160,
                                     blank=True, null=True)
    razao_social = models.CharField("Razao social", max_length=160,
                                    blank=True, null=True)
    cnpj = models.CharField("CNPJ", validators=[MinLengthValidator(14)], max_length=14)
    lotes = models.ManyToManyField(Lote, related_name="lotes")

    representante_legal = models.CharField("Representante legal", max_length=160,
                                           blank=True, null=True)
    representante_contato = models.CharField("Representante contato (email/tel)", max_length=160,
                                             blank=True, null=True)
    nutricionista_responsavel = models.CharField("Nutricionista responsavel", max_length=160,
                                                 blank=True, null=True)
    nutricionista_crn = models.CharField("Nutricionista crn", max_length=160,
                                         blank=True, null=True)

    endereco = models.ForeignKey("dados_comuns.Endereco", on_delete=models.CASCADE,
                                 blank=True, null=True)
    contato = models.ForeignKey("dados_comuns.Contato", on_delete=models.CASCADE,
                                blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.nome_fantasia, self.cnpj)

    class Meta:
        verbose_name = "Terceirizada"
        verbose_name_plural = "Terceirizadas"
