from django.core.validators import MinLengthValidator
from django.db import models

from ..dados_comuns.models_abstract import (
    Descritivel, IntervaloDeDia,
    TemChaveExterna, Nomeavel, Ativavel,
    TemIdentificadorExternoAmigavel)


from ..escola.models import (
    Lote,
    DiretoriaRegional
)


class Edital(TemChaveExterna):
    numero = models.CharField("Edital No", max_length=100, help_text="Número do Edital", unique=True)
    tipo_contratacao = models.CharField("Tipo de contratação", max_length=100)
    processo = models.CharField("Processo Administrativo", max_length=100,
                                help_text="Processo administrativo do edital")
    objeto = models.TextField("objeto resumido")

    @property
    def contratos(self):
        return self.contratos

    def __str__(self):
        return f"{self.numero} - {self.objeto}"

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

    def __str__(self):
        return f"{self.nome_fantasia}"

    class Meta:
        verbose_name = "Terceirizada"
        verbose_name_plural = "Terceirizadas"


class Contrato(TemChaveExterna):
    numero = models.CharField("No do contrato", max_length=100)
    processo = models.CharField("Processo Administrativo", max_length=100,
                                help_text="Processo administrativo do contrato")
    data_proposta = models.DateField("Data da proposta")
    lotes = models.ManyToManyField(Lote, related_name="contratos_do_lote")
    terceirizadas = models.ManyToManyField(Terceirizada, related_name="contratos_da_terceirizada")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="contratos", blank=True, null=True)
    dres = models.ManyToManyField(DiretoriaRegional, related_name="contratos_da_dre")

    def __str__(self):
        return f"Contrato:{self.numero} Processo: {self.processo}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"


class VigenciaContrato(TemChaveExterna, IntervaloDeDia):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="vigencias", null=True, blank=True)

    def __str__(self):
        return f"Contrato:{self.contrato.numero} {self.data_inicial} a {self.data_final}"

    class Meta:
        verbose_name = "Vigência de contrato"
        verbose_name_plural = "Vigências de contrato"

