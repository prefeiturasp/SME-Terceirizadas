from django.core.validators import MinLengthValidator
from django.db import models

from ...dados_comuns.behaviors import ModeloBase


class SolicitacaoRemessaManager(models.Manager):

    def create_solicitacao(self, StrCnpj, StrNumSol):
        return self.create(
            cnpj=StrCnpj,
            numero_solicitacao=StrNumSol
        )


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
        'Status da solicitação',
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_INTEGRADA
    )

    objects = SolicitacaoRemessaManager()

    def __str__(self):
        return f'Solicitação: {self.numero_solicitacao} - Status: {self.status}'

    class Meta:
        verbose_name = 'Solicitação Remessa'
        verbose_name_plural = 'Solicitações Remessas'
