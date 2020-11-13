from django.db import models

from ...dados_comuns.behaviors import ModeloBase
from .solicitacao import SolicitacaoRemessa


class GuiaManager(models.Manager):

    def create_guia(self, StrNumGui, DtEntrega, StrCodUni, StrNomUni,
                    StrEndUni, StrNumUni, StrBaiUni, StrCepUni,
                    StrCidUni, StrEstUni, StrConUni, StrTelUni,
                    solicitacao):
        return self.create(
            numero_guia=StrNumGui,
            data_entrega=DtEntrega,
            codigo_unidade=StrCodUni,
            nome_unidade=StrNomUni,
            endereco_unidade=StrEndUni,
            numero_unidade=StrNumUni,
            bairro_unidade=StrBaiUni,
            cep_unidade=StrCepUni,
            cidade_unidade=StrCidUni,
            estado_unidade=StrEstUni,
            contato_unidade=StrConUni,
            telefone_unidade=StrTelUni,
            solicitacao=solicitacao
        )


class Guia(ModeloBase):
    # Status Choice
    STATUS_INTEGRADA = 'INTEGRADA'

    STATUS_NOMES = {
        STATUS_INTEGRADA: 'Integrada',
    }

    STATUS_CHOICES = (
        (STATUS_INTEGRADA, STATUS_NOMES[STATUS_INTEGRADA]),
    )

    numero_guia = models.CharField('Número da guia', blank=True, max_length=100)
    solicitacao = models.ForeignKey(
        SolicitacaoRemessa, on_delete=models.CASCADE, blank=True, null=True, related_name='guias')
    data_entrega = models.DateField('Data da entrega')
    codigo_unidade = models.CharField('Código da unidade', blank=True, max_length=10)
    nome_unidade = models.CharField('Nome da unidade', blank=True, max_length=150)
    endereco_unidade = models.CharField('Endereço da unidade', blank=True, max_length=300)
    numero_unidade = models.CharField('Número da unidade', blank=True, max_length=10)
    bairro_unidade = models.CharField('Bairro da unidade', blank=True, max_length=100)
    cep_unidade = models.CharField('CEP da unidade', blank=True, max_length=20)
    cidade_unidade = models.CharField('Cidade da unidade', blank=True, max_length=100)
    estado_unidade = models.CharField('Estado da unidade', blank=True, max_length=2)
    contato_unidade = models.CharField('Contato na unidade', blank=True, max_length=150)
    telefone_unidade = models.CharField('Telefone da unidade', blank=True, default='', max_length=20)
    status = models.CharField(
        'Status da guia',
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_INTEGRADA
    )

    objects = GuiaManager()

    def __str__(self):
        return f'Guia: {self.numero_guia} - {self.status} da solicitação: {self.solicitacao.numero_solicitacao}'

    class Meta:
        verbose_name = 'Guia de Remessa'
        verbose_name_plural = 'Guias de Remessas'
