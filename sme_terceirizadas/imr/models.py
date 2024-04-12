import os

from django.apps import apps
from django.core.validators import FileExtensionValidator
from django.db import models

from ..cardapio.models import TipoAlimentacao
from ..dados_comuns.behaviors import (
    CriadoPor,
    ModeloBase,
    Nomeavel,
    PerfilDiretorSupervisao,
    Posicao,
    StatusAtivoInativo,
)
from ..dados_comuns.validators import validate_file_size_10mb
from ..perfil.models import Usuario


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
        verbose_name="Tipo de Penalidade",
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
        verbose_name="Categoria da Ocorrência",
        on_delete=models.PROTECT,
        related_name="tipos_ocorrencia",
    )
    titulo = models.CharField("Titulo", max_length=100)
    descricao = models.TextField("Descrição")
    penalidade = models.ForeignKey(
        TipoPenalidade,
        verbose_name="Penalidade do Item",
        on_delete=models.PROTECT,
        related_name="tipos_ocorrencia",
    )
    pontuacao = models.PositiveSmallIntegerField(
        "Pontuação (IMR)", blank=True, null=True
    )
    tolerancia = models.PositiveSmallIntegerField("Tolerância", blank=True, null=True)
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


class Relatorio(ModeloBase):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="relatorios"
    )
    data = models.DateField()


class TipoPerguntaParametrizacaoOcorrencia(ModeloBase, Nomeavel):
    RESPOSTA_SIM_NAO = "RespostaSimNao"
    RESPOSTA_TIPO_ALIMENTACAO = "RespostaTipoAlimentacao"

    TIPOS_RESPOSTA = (
        (RESPOSTA_SIM_NAO, RESPOSTA_SIM_NAO),
        (RESPOSTA_TIPO_ALIMENTACAO, RESPOSTA_TIPO_ALIMENTACAO),
    )

    tipo_resposta = models.CharField(
        "Tipo de resposta", choices=TIPOS_RESPOSTA, max_length=100
    )

    def get_model_tipo_resposta(self):
        return apps.get_model("imr", self.tipo_resposta)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        verbose_name = "Tipo de Pergunta para Parametrização de Tipo de Ocorrência"
        verbose_name_plural = (
            "Tipos de Pergunta para Parametrização de Tipo de Ocorrência"
        )


class ParametrizacaoOcorrencia(ModeloBase, Posicao):
    titulo = models.CharField("Titulo", max_length=100)
    tipo_ocorrencia = models.ForeignKey(
        TipoOcorrencia, on_delete=models.PROTECT, related_name="parametrizacoes"
    )
    tipo_pergunta = models.ForeignKey(
        TipoPerguntaParametrizacaoOcorrencia,
        on_delete=models.PROTECT,
        related_name="parametrizacoes",
    )

    def __str__(self):
        return f"{self.tipo_ocorrencia.__str__()} {self.tipo_pergunta} - {self.posicao}"

    class Meta:
        verbose_name = "Parametrização de Tipo de Ocorrência"
        verbose_name_plural = "Parametrizações de Tipo de Ocorrência"


class RespostaSimNao(ModeloBase):
    SIM = "Sim"
    NAO = "Não"

    CHOICES = ((SIM, SIM), (NAO, NAO))
    resposta = models.CharField("Opção", choices=CHOICES, max_length=3)
    relatorio = models.ForeignKey(
        Relatorio, on_delete=models.CASCADE, related_name="respostas_sim_nao"
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_sim_nao",
    )

    def __str__(self):
        return self.resposta

    class Meta:
        verbose_name = "Resposta Sim/Não"
        verbose_name_plural = "Respostas Sim/Não"


class RespostaTipoAlimentacao(ModeloBase):
    resposta = models.ForeignKey(
        TipoAlimentacao,
        on_delete=models.PROTECT,
        related_name="respostas_relatorio_imr",
    )
    relatorio = models.ForeignKey(
        Relatorio, on_delete=models.CASCADE, related_name="respostas_tipos_alimentacao"
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_tipos_alimentacao",
    )

    def __str__(self):
        return self.resposta.nome

    class Meta:
        verbose_name = "Resposta Tipo Alimentação"
        verbose_name_plural = "Respostas Tipo Alimentação"
