import os

from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
    ValidationError,
)
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
from ..escola.models import Escola, FaixaEtaria, PeriodoEscolar
from ..medicao_inicial.models import SolicitacaoMedicaoInicial
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
    eh_imr = models.BooleanField("É IMR?", default=False)
    pontuacao = models.PositiveSmallIntegerField(
        "Pontuação (IMR)", blank=True, null=True
    )
    tolerancia = models.PositiveSmallIntegerField("Tolerância", blank=True, null=True)
    porcentagem_desconto = models.FloatField(
        "% de desconto",
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Caso a opção de É IMR? esteja marcada a % de desconto incidirá sobre a reincidência dos apontamentos. Se não for marcada a opção de É IMR?, a % de desconto será referente a multa da penalidade.",
    )
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

    def valida_eh_imr(self, dict_error):
        if self.eh_imr and (not self.pontuacao or not self.tolerancia):
            if not self.pontuacao:
                dict_error["pontuacao"] = "Pontuação deve ser preenchida se for IMR."
            if not self.tolerancia:
                dict_error["tolerancia"] = "Tolerância deve ser preenchida se for IMR."
        return dict_error

    def valida_nao_eh_imr(self, dict_error):
        if not self.eh_imr and (self.pontuacao or self.tolerancia):
            if self.pontuacao:
                dict_error["pontuacao"] = "Pontuação só deve ser preenchida se for IMR."
            if self.tolerancia:
                dict_error[
                    "tolerancia"
                ] = "Tolerância só deve ser preenchida se for IMR."
        return dict_error

    def clean(self):
        super().clean()
        dict_error = {}
        dict_error = self.valida_eh_imr(dict_error)
        dict_error = self.valida_nao_eh_imr(dict_error)
        raise ValidationError(dict_error)

    def delete(self, *args, **kwargs):
        if self.modelo_anexo:
            if os.path.isfile(self.modelo_anexo.path):
                os.remove(self.modelo_anexo.path)
        super().delete(*args, **kwargs)


class TipoRespostaModelo(ModeloBase, Nomeavel):
    def __str__(self):
        return f"{self.nome}"

    class Meta:
        verbose_name = "Tipo de Resposta (Modelo)"
        verbose_name_plural = "Tipos de Resposta (Modelo)"


class TipoPerguntaParametrizacaoOcorrencia(ModeloBase, Nomeavel):
    tipo_resposta = models.OneToOneField(
        TipoRespostaModelo, verbose_name="Tipo de resposta", on_delete=models.CASCADE
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


class PeriodoVisita(ModeloBase, Nomeavel):
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Período de Visita"
        verbose_name_plural = "Períodos de Visita"


class FormularioOcorrenciasBase(ModeloBase):
    usuario = models.ForeignKey(
        Usuario,
        verbose_name="Usuário",
        on_delete=models.PROTECT,
        related_name="formularios_ocorrencias",
    )
    data = models.DateField()

    def __str__(self):
        return f"{self.usuario.nome} - {self.data}"

    class Meta:
        verbose_name = "Formulário Base - Ocorrências"
        verbose_name_plural = "Formulários Base - Ocorrências"


class FormularioDiretor(ModeloBase):
    formulario_base = models.OneToOneField(
        FormularioOcorrenciasBase, on_delete=models.CASCADE
    )
    solicitacao_medicao_inicial = models.ForeignKey(
        SolicitacaoMedicaoInicial,
        verbose_name="Solicitação Medição Inicial",
        on_delete=models.PROTECT,
        related_name="formularios_ocorrencias",
    )

    def __str__(self):
        return f"{self.solicitacao_medicao_inicial.escola.nome} - {self.formulario_base.data}"

    class Meta:
        verbose_name = "Formulário do Diretor - Ocorrências"
        verbose_name_plural = "Formulários do Diretor - Ocorrências"


class FormularioSupervisao(ModeloBase):
    escola = models.ForeignKey(
        Escola, on_delete=models.PROTECT, related_name="formularios_supervisao"
    )
    formulario_base = models.OneToOneField(
        FormularioOcorrenciasBase, on_delete=models.CASCADE
    )
    periodo_visita = models.ForeignKey(
        PeriodoVisita,
        verbose_name="Período da Visita",
        on_delete=models.PROTECT,
        related_name="formularios_supervisao",
    )
    nome_nutricionista_empresa = models.CharField(
        "Nome da Nutricionista RT da Empresa", max_length=100
    )
    acompanhou_visita = models.BooleanField("Acompanhou a visita?", default=False)
    apresentou_ocorrencias = models.BooleanField(
        "No momento da visita, a prestação de serviços apresentou ocorrências?",
        default=False,
    )

    def __str__(self):
        return f"{self.escola.nome} - {self.formulario_base.data}"

    class Meta:
        verbose_name = "Formulário da Supervisão - Ocorrências"
        verbose_name_plural = "Formulários da Supervisão - Ocorrências"


class RespostaSimNao(ModeloBase):
    SIM = "Sim"
    NAO = "Não"

    CHOICES = ((SIM, SIM), (NAO, NAO))
    resposta = models.CharField("Opção", choices=CHOICES, max_length=3)
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_sim_nao",
        null=True,
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


class RespostaCampoNumerico(ModeloBase):
    resposta = models.FloatField()
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_campo_numerico",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_campo_numerico",
    )

    def __str__(self):
        return str(self.resposta)

    class Meta:
        verbose_name = "Resposta Campo Numérico"
        verbose_name_plural = "Respostas Campo Numérico"


class RespostaCampoTextoSimples(ModeloBase):
    resposta = models.CharField(max_length=500)
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_campo_texto_simples",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_campo_texto_simples",
    )

    def __str__(self):
        return self.resposta

    class Meta:
        verbose_name = "Resposta Campo Texto Simples"
        verbose_name_plural = "Respostas Campo Texto Simples"


class RespostaCampoTextoLongo(ModeloBase):
    resposta = models.TextField()
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_campo_texto_longo",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_campo_texto_longo",
    )

    def __str__(self):
        return self.resposta

    class Meta:
        verbose_name = "Resposta Campo Texto Longo"
        verbose_name_plural = "Respostas Campo Texto Longo"


class RespostaDatas(ModeloBase):
    resposta = ArrayField(models.DateField())
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_datas",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_datas",
    )

    def __str__(self):
        return str(self.resposta)

    class Meta:
        verbose_name = "Resposta Datas"
        verbose_name_plural = "Respostas Datas"


class RespostaPeriodo(ModeloBase):
    resposta = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        related_name="respostas_relatorio_imr",
    )
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_periodo",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_periodo",
    )

    def __str__(self):
        return self.resposta.nome

    class Meta:
        verbose_name = "Resposta Período"
        verbose_name_plural = "Respostas Período"


class RespostaFaixaEtaria(ModeloBase):
    resposta = models.ForeignKey(
        FaixaEtaria,
        on_delete=models.PROTECT,
        related_name="respostas_relatorio_imr",
    )
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_faixa_etaria",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_faixa_etaria",
    )

    def __str__(self):
        return self.resposta.nome

    class Meta:
        verbose_name = "Resposta Faixa Etária"
        verbose_name_plural = "Respostas Faixa Etária"


class RespostaTipoAlimentacao(ModeloBase):
    resposta = models.ForeignKey(
        TipoAlimentacao,
        on_delete=models.PROTECT,
        related_name="respostas_relatorio_imr",
    )
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_tipos_alimentacao",
        null=True,
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


class RespostaSimNaoNaoSeAplica(ModeloBase):
    SIM = "Sim"
    NAO = "Não"
    NAO_SE_APLICA = "Não se aplica"

    CHOICES = ((SIM, SIM), (NAO, NAO), (NAO_SE_APLICA, NAO_SE_APLICA))
    resposta = models.CharField("Opção", choices=CHOICES, max_length=13)
    formulario_base = models.ForeignKey(
        FormularioOcorrenciasBase,
        verbose_name="Formulário de Ocorrências",
        on_delete=models.CASCADE,
        related_name="respostas_sim_nao_nao_se_aplica",
        null=True,
    )
    parametrizacao = models.ForeignKey(
        ParametrizacaoOcorrencia,
        on_delete=models.CASCADE,
        related_name="respostas_sim_nao_nao_se_aplica",
    )

    def __str__(self):
        return self.resposta

    class Meta:
        verbose_name = "Resposta Sim/Não/Não se aplica"
        verbose_name_plural = "Respostas Sim/Não/Não se aplica"


class FaixaPontuacaoIMR(ModeloBase):
    pontuacao_minima = models.PositiveSmallIntegerField("Pontuação Mínima")
    pontuacao_maxima = models.PositiveSmallIntegerField(
        "Pontuação Máxima", blank=True, null=True
    )
    porcentagem_desconto = models.FloatField(
        "% de Desconto",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Desconto no faturamento do dia",
    )

    def clean(self):
        super().clean()
        faixas = list(
            FaixaPontuacaoIMR.objects.exclude(uuid=self.uuid).values_list(
                "pontuacao_minima", "pontuacao_maxima"
            )
        )
        dict_error = {}
        if any(
            faixa[0] <= self.pontuacao_minima <= (faixa[1] or faixa[0])
            for faixa in faixas
        ):
            dict_error[
                "pontuacao_minima"
            ] = "Esta pontuação mínima já se encontra dentro de outra faixa."
        if self.pontuacao_maxima and any(
            faixa[0] <= self.pontuacao_maxima <= (faixa[1] or faixa[0])
            for faixa in faixas
        ):
            dict_error[
                "pontuacao_maxima"
            ] = "Esta pontuação máxima já se encontra dentro de outra faixa."
        raise ValidationError(dict_error)

    def __str__(self):
        return (
            f"{self.pontuacao_minima} - {self.pontuacao_maxima or 'sem pontuação máxima'}"
            f" - {self.porcentagem_desconto}"
        )

    class Meta:
        verbose_name = "Faixa de Pontuação - IMR"
        verbose_name_plural = "Faixas de Pontuação - IMR"
        ordering = ("pontuacao_minima",)
