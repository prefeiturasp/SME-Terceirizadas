from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField

from ..dados_comuns.behaviors import ModeloBase


class QuestaoConferencia(ModeloBase):
    # Tipo Questão Choice
    TIPO_QUESTAO_PRIMARIA = "PRIMARIA"
    TIPO_QUESTAO_SECUNDARIA = "SECUNDARIA"

    TIPO_QUESTAO_NOMES = {
        TIPO_QUESTAO_PRIMARIA: "Primária",
        TIPO_QUESTAO_SECUNDARIA: "Secundária",
    }

    TIPO_QUESTAO_CHOICES = (
        (TIPO_QUESTAO_PRIMARIA, TIPO_QUESTAO_NOMES[TIPO_QUESTAO_PRIMARIA]),
        (TIPO_QUESTAO_SECUNDARIA, TIPO_QUESTAO_NOMES[TIPO_QUESTAO_SECUNDARIA]),
    )

    # status choice
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"

    STATUS_CHOICES = (
        (ATIVO, "Ativo"),
        (INATIVO, "Inativo"),
    )

    questao = models.CharField("Questão")
    tipo_questao = MultiSelectField("Tipo de Questão", choices=TIPO_QUESTAO_CHOICES)
    pergunta_obrigatoria = models.BooleanField("Pergunta Obrigatória?", default=False)
    posicao = models.PositiveSmallIntegerField("Posição", blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=ATIVO)

    def __str__(self):
        return f"{self.questao}"

    class Meta:
        verbose_name = "Questão para Conferência"
        verbose_name_plural = "Questões para Conferência"

    def clean(self):
        super().clean()
        if self.pergunta_obrigatoria and not self.posicao:
            raise ValidationError(
                {"posicao": "Posição é obrigatória se a pergunta for obrigatória."}
            )