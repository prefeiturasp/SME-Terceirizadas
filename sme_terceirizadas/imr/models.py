import os

from django.core.validators import FileExtensionValidator
from django.db import models

from ..dados_comuns.behaviors import (
    CriadoPor,
    ModeloBase,
    Nomeavel,
    PerfilDiretorSupervisao,
    Posicao,
    StatusAtivoInativo,
)
from ..dados_comuns.validators import validate_file_size_10mb


class TipoGravidade(ModeloBase):
    tipo = models.CharField("Tipo de Gravidade")

    def __str__(self):
        return f"{self.tipo}"

    class Meta:
        verbose_name = "Tipo de Gravidade"
        verbose_name_plural = "Tipos de Gravidades"


class TipoPenalidade(ModeloBase, CriadoPor, StatusAtivoInativo):
    edital = models.ForeignKey(
        "terceirizada.Edital",
        on_delete=models.PROTECT,
        related_name="tipos_penalidades",
    )
    numero_clausula = models.CharField("Número da Cláusula/Item", max_length=300)
    gravidade = models.ForeignKey(
        TipoGravidade, on_delete=models.PROTECT, related_name="tipos_penalidades"
    )
    descricao = models.TextField("Descrição da Cláusula/Item")

    def __str__(self):
        return f"Item: {self.numero_clausula} - Edital: {self.edital.numero}"

    class Meta:
        verbose_name = "Tipo de Penalidade"
        verbose_name_plural = "Tipos de Penalidades"


class ObrigacaoPenalidade(ModeloBase):
    tipo_penalidade = models.ForeignKey(
        TipoPenalidade,
        on_delete=models.CASCADE,
        related_name="obrigacoes",
    )
    descricao = models.CharField("Descrição", max_length=300)

    def __str__(self):
        return f"{self.descricao}"

    class Meta:
        verbose_name = "Obrigação da Penalidade"
        verbose_name_plural = "Obrigações das Penalidades"


class CategoriaOcorrencia(ModeloBase, Nomeavel, Posicao, PerfilDiretorSupervisao):
    def __str__(self):
        return f"{self.nome}"

    class Meta:
        verbose_name = "Categoria das Ocorrências"
        verbose_name_plural = "Categorias das Ocorrências"


class TipoOcorrencia(
    ModeloBase, CriadoPor, Posicao, PerfilDiretorSupervisao, StatusAtivoInativo
):
    edital = models.ForeignKey(
        "terceirizada.Edital",
        on_delete=models.PROTECT,
        related_name="tipos_ocorrencia",
    )
    categoria = models.ForeignKey(
        CategoriaOcorrencia,
        on_delete=models.PROTECT,
        related_name="tipos_ocorrencia",
    )
    titulo = models.CharField("Titulo", max_length=100)
    descricao = models.TextField("Descrição")
    penalidade = models.ForeignKey(
        TipoPenalidade, on_delete=models.PROTECT, related_name="tipos_ocorrencia"
    )
    pontuacao = models.PositiveSmallIntegerField(blank=True, null=True)
    tolerancia = models.PositiveSmallIntegerField(blank=True, null=True)
    modelo_anexo = models.FileField(
        "Modelo de Anexo",
        upload_to="IMR",
        validators=[
            FileExtensionValidator(allowed_extensions=["XLS", "XLSX"]),
            validate_file_size_10mb,
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.edital.numero} - {self.titulo}"

    class Meta:
        verbose_name = "Tipo de Ocorrência"
        verbose_name_plural = "Tipos de Ocorrência"

    def delete(self, *args, **kwargs):
        if self.modelo_anexo:
            if os.path.isfile(self.modelo_anexo.path):
                os.remove(self.modelo_anexo.path)
        super().delete(*args, **kwargs)


class ParametrizacaoOcorrencia(ModeloBase, Posicao):
    OPCOES_SIM_NAO = "Opções Sim/Não"
    CAMPO_NUMERICO = "Campo Numérico"
    CAMPO_TEXTO_SIMPLES = "Campo de Texto Simples"
    CAMPO_TEXTO_LONGO = "Campo de Texto Longo"
    SELETOR_DATAS = "Seletor de Datas"
    SELETOR_PERIODOS = "Seletor de Períodos"
    SELETOR_FAIXAS_ETARIAS = "Seletor de Faixas Etárias"
    SELETOR_TIPO_ALIMENTACAO = "Seletor de Tipo de Alimentação"
    SELETOR_SIM_NAO_NAO_SE_APLICE = "Seletor de Sim/Não/Não se aplica"

    CHOICES = (
        (OPCOES_SIM_NAO, OPCOES_SIM_NAO),
        (CAMPO_NUMERICO, CAMPO_NUMERICO),
        (CAMPO_TEXTO_SIMPLES, CAMPO_TEXTO_SIMPLES),
        (CAMPO_TEXTO_LONGO, CAMPO_TEXTO_LONGO),
        (SELETOR_DATAS, SELETOR_DATAS),
        (SELETOR_PERIODOS, SELETOR_PERIODOS),
        (SELETOR_FAIXAS_ETARIAS, SELETOR_FAIXAS_ETARIAS),
        (SELETOR_TIPO_ALIMENTACAO, SELETOR_TIPO_ALIMENTACAO),
        (SELETOR_SIM_NAO_NAO_SE_APLICE, SELETOR_SIM_NAO_NAO_SE_APLICE),
    )

    titulo = models.CharField("Titulo", max_length=100)
    tipo_ocorrencia = models.ForeignKey(
        TipoOcorrencia, on_delete=models.PROTECT, related_name="parametrizacoes"
    )
    tipo_resposta = models.CharField("Tipo de resposta", choices=CHOICES)

    def __str__(self):
        return f"{self.tipo_ocorrencia.__str__()} {self.tipo_resposta} - {self.posicao}"

    class Meta:
        verbose_name = "Parametrização de Tipo de Ocorrência"
        verbose_name_plural = "Parametrizações de Tipo de Ocorrência"
