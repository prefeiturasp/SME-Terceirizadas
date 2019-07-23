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
        verbose_name = "Edital"
        verbose_name_plural = "Editais"


class Terceirizada(TemChaveExterna, Ativavel):
    """Empresa Terceirizada"""

    nome_fantasia = models.CharField("Nome fantasia", max_length=160,
                                     blank=True, null=True)
    razao_social = models.CharField("Razao social", max_length=160,
                                    blank=True, null=True)
    cnpj = models.CharField("CNPJ", validators=[MinLengthValidator(14)], max_length=14)
    lotes = models.ManyToManyField("escola.Lote", related_name="lotes")

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
