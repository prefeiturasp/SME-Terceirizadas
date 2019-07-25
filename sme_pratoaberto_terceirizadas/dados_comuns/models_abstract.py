import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_xworkflows import models as xwf_models
from model_utils import Choices

from .fluxo_status import PedidoAPartirDaEscolaWorkflow, PedidoAPartirDaDiretoriaRegionalWorkflow


class Iniciais(models.Model):
    iniciais = models.CharField("Iniciais", blank=True, null=True, max_length=10)

    class Meta:
        abstract = True


class Descritivel(models.Model):
    descricao = models.TextField("Descricao", blank=True, null=True)

    class Meta:
        abstract = True


class Nomeavel(models.Model):
    nome = models.CharField("Nome", blank=True, null=True, max_length=50)

    class Meta:
        abstract = True


class Motivo(models.Model):
    motivo = models.TextField("Motivo", blank=True, null=True)

    class Meta:
        abstract = True


class Ativavel(models.Model):
    ativo = models.BooleanField("Está ativo?", default=True)

    class Meta:
        abstract = True


class CriadoEm(models.Model):
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)

    class Meta:
        abstract = True


class IntervaloDeTempo(models.Model):
    data_hora_inicial = models.DateTimeField("Data/hora inicial")
    data_hora_final = models.DateTimeField("Data/hora final")

    class Meta:
        abstract = True


class IntervaloDeDia(models.Model):
    data_inicial = models.DateField("Data inicial")
    data_final = models.DateField("Data final")

    class Meta:
        abstract = True


class TemData(models.Model):
    data = models.DateField("Data")

    class Meta:
        abstract = True


class TemChaveExterna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class StatusValidacao(models.Model):
    """
     - https://steelkiwi.com/blog/best-practices-working-django-models-python/
     - https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63
    """
    STATUSES = Choices(
        (0, 'DRE_A_VALIDAR', 'A validar pela DRE'),
        (1, 'DRE_APROVADO', 'Aprovado pela DRE'),
        (2, 'DRE_REPROVADO', 'Reprovado pela DRE'),
        (3, 'CODAE_A_VALIDAR', 'A validar pela CODAE'),  # QUANDO A DRE VALIDA
        (4, 'CODAE_APROVADO', 'Aprovado pela CODAE'),  # CODAE RECEBE
        (5, 'CODAE_REPROVADO', 'Reprovado pela CODAE'),
        (6, 'TERCEIRIZADA_A_VISUALIZAR', 'Terceirizada a visualizar'),
        (7, 'TERCEIRIZADA_A_VISUALIZADO', 'Terceirizada visualizado')  # TOMOU CIENCIA, TODOS DEVEM FICAR SABENDO...
    )
    status = models.IntegerField(choices=STATUSES, default=STATUSES.DRE_A_VALIDAR)

    class Meta:
        abstract = True


class DiasSemana(models.Model):
    SEGUNDA = 0
    TERCA = 1
    QUARTA = 2
    QUINTA = 3
    SEXTA = 4
    SABADO = 5
    DOMINGO = 6

    DIAS = (
        (SEGUNDA, 'Segunda'),
        (TERCA, 'Terça'),
        (QUINTA, 'Quarta'),
        (QUARTA, 'Quinta'),
        (SEXTA, 'Sexta'),
        (SABADO, 'Sábado'),
        (DOMINGO, 'Domingo'),
    )

    dias_semana = ArrayField(
        models.PositiveSmallIntegerField(choices=DIAS,
                                         default=[],
                                         null=True, blank=True
                                         )
    )

    def dias_semana_display(self):
        result = ''
        choices = dict(self.DIAS)
        for index, value in enumerate(self.dias_semana):
            result += "{0}".format(choices[value])
            if not index == len(self.dias_semana) - 1:
                result += ', '
        return result

    class Meta:
        abstract = True


class TempoPasseio(models.Model):
    QUATRO = 0
    CINCO_A_SETE = 1
    OITO_OU_MAIS = 2

    HORAS = (
        (QUATRO, 'Quatro horas'),
        (CINCO_A_SETE, 'Cinco a sete horas'),
        (OITO_OU_MAIS, 'Oito horas'),
    )
    tempo_passeio = models.PositiveSmallIntegerField(choices=HORAS,
                                                     null=True, blank=True)

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaEscolaWorkflow

    status = xwf_models.StateField(workflow_class)

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status == self.workflow_class.DRE_A_VALIDAR

    @property
    def ta_na_escola(self):
        return self.status in [self.workflow_class.RASCUNHO,
                               self.workflow_class.DRE_PEDE_ESCOLA_REVISAR]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.DRE_APROVADO

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_APROVADO

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaDiretoriaRegional(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaDiretoriaRegionalWorkflow
    status = xwf_models.StateField(workflow_class)

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status in [self.workflow_class.CODAE_PEDE_DRE_REVISAR,
                               self.workflow_class.RASCUNHO]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.CODAE_A_VALIDAR

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_APROVADO

    class Meta:
        abstract = True


class CriadoPor(models.Model):
    # TODO: futuramente deixar obrigatorio esse campo
    criado_por = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING,
                                   null=True, blank=True)

    class Meta:
        abstract = True
