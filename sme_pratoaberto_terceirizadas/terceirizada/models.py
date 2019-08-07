from django.core.validators import MinLengthValidator
from django.db import models

from ..dados_comuns.models_abstract import (
    Descritivel, IntervaloDeDia,
    TemChaveExterna, Nomeavel, Ativavel,
    TemIdentificadorExternoAmigavel)


class Edital(TemChaveExterna, Nomeavel, Descritivel, Ativavel, IntervaloDeDia):

    def __str__(self):
        return f"{self.nome} válido de {self.data_inicial} até {self.data_final}"

    class Meta:
        verbose_name = "Edital"
        verbose_name_plural = "Editais"


class Nutricionista(TemChaveExterna, Nomeavel):
    # TODO: verificar a diferença dessa pra nutricionista da CODAE

    crn_numero = models.CharField("Nutricionista crn", max_length=160,
                                  blank=True, null=True)
    terceirizada = models.ForeignKey('Terceirizada',
                                     on_delete=models.CASCADE,
                                     related_name='nutricionistas',
                                     blank=True,
                                     null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Nutricionista"
        verbose_name_plural = "Nutricionistas"


class Terceirizada(TemChaveExterna, Ativavel, TemIdentificadorExternoAmigavel):
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
    endereco = models.ForeignKey("dados_comuns.Endereco", on_delete=models.CASCADE,
                                 blank=True, null=True)
    # TODO: criar uma tabela central (Instituição) para agregar Escola, DRE, Terc e CODAE???
    # e a partir dai a instituição que tem contatos e endereço?
    # o mesmo para pessoa fisica talvez?
    contatos = models.ManyToManyField("dados_comuns.Contato", blank=True)

    @property
    def nutricionistas(self):
        return self.nutricionistas

    class Meta:
        verbose_name = "Terceirizada"
        verbose_name_plural = "Terceirizadas"
