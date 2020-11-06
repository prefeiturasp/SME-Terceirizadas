from django.core.validators import MinLengthValidator
from django.db import models

from ...dados_comuns.behaviors import ModeloBase


class SolicitacaoRemessa(ModeloBase):
    # Status Choice
    STATUS_INTEGRADA = 'INTEGRADA'

    STATUS_NOMES = {
        STATUS_INTEGRADA: 'Integrada',
    }

    STATUS_CHOICES = (
        (STATUS_INTEGRADA, STATUS_NOMES[STATUS_INTEGRADA]),
    )
    cnpj = models.CharField('CNPJ', validators=[MinLengthValidator(14)], max_length=14)
    numero_solicitacao = models.CharField('Número da solicitação', blank=True, max_length=100)
    status = models.CharField(
        'status',
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_INTEGRADA
    )

    class Meta:
        verbose_name = "Solicitação Remessa"
        verbose_name_plural = "Solicitações Remessas"
