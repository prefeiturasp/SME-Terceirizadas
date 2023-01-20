from django.db import models

from ...dados_comuns.behaviors import Logs, ModeloBase, TemIdentificadorExternoAmigavel
from ...dados_comuns.fluxo_status import FluxoCronograma
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...produto.models import NomeDeProdutoEdital, UnidadeMedida
from ...terceirizada.models import Contrato, Terceirizada


class Cronograma(ModeloBase, TemIdentificadorExternoAmigavel, Logs, FluxoCronograma):

    CAIXA = 'CAIXA'
    FARDO = 'FARDO'
    TUBET = 'TUBET'

    TIPO_EMBALAGEM_CHOICES = (
        (CAIXA, 'Caixa'),
        (FARDO, 'Fardo'),
        (TUBET, 'Tubet'),
    )

    numero = models.CharField('Número do Cronograma', blank=True, max_length=50, unique=True)
    # Criar validate pra ver se contrato pertence a empresa
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, blank=True, null=True)
    empresa = models.ForeignKey(
        Terceirizada, on_delete=models.CASCADE, blank=True, null=True)
    produto = models.ForeignKey(
        NomeDeProdutoEdital, on_delete=models.CASCADE, blank=True, null=True)
    qtd_total_programada = models.FloatField('Qtd Total Programada', blank=True, null=True)
    unidade_medida = models.ForeignKey(
        UnidadeMedida, on_delete=models.PROTECT, blank=True, null=True)
    armazem = models.ForeignKey(
        Terceirizada, on_delete=models.CASCADE, blank=True, null=True, related_name='cronogramas')
    tipo_embalagem = models.CharField(choices=TIPO_EMBALAGEM_CHOICES, max_length=15, blank=True)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.CRONOGRAMA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    def __str__(self):
        return f'Cronograma: {self.numero} - Status: {self.get_status_display()}'

    class Meta:
        verbose_name = 'Cronograma'
        verbose_name_plural = 'Cronogramas'


class EtapasDoCronograma(ModeloBase):
    cronograma = models.ForeignKey(
        Cronograma, on_delete=models.CASCADE, blank=True, null=True, related_name='etapas')
    numero_empenho = models.CharField('Número do Empenho', blank=True, max_length=50)
    etapa = models.CharField(blank=True, max_length=15)
    parte = models.CharField(blank=True, max_length=15)
    data_programada = models.DateField('Data Programada', blank=True, null=True)
    quantidade = models.FloatField(blank=True, null=True)
    total_embalagens = models.PositiveSmallIntegerField('Total de Embalagens', blank=True, null=True)

    def __str__(self):
        if self.etapa:
            return f'{self.etapa} do cronogrma {self.cronograma.numero}'
        else:
            return f'Etapa do cronogrma {self.cronograma.numero}'

    class Meta:
        ordering = ('etapa', 'data_programada')
        verbose_name = 'Etapa do Cronograma'
        verbose_name_plural = 'Etapas dos Cronogramas'

    @classmethod
    def etapas_to_json(cls):
        result = []
        for numero in range(1, 101):
            choice = {
                'uuid': f'Etapa {numero}',
                'value': f'Etapa {numero}'
            }
            result.append(choice)
        return result


class ProgramacaoDoRecebimentoDoCronograma(ModeloBase):
    PALETIZADA = 'PALETIZADA'
    ESTIVADA_BATIDA = 'ESTIVADA_BATIDA'

    TIPO_CARGA_CHOICES = (
        (PALETIZADA, 'Paletizada'),
        (ESTIVADA_BATIDA, 'Estivada / Batida'),
    )

    cronograma = models.ForeignKey(
        Cronograma, on_delete=models.CASCADE, blank=True, null=True, related_name='programacoes_de_recebimento')
    data_programada = models.CharField(blank=True, max_length=50)
    tipo_carga = models.CharField(choices=TIPO_CARGA_CHOICES, max_length=20, blank=True)

    def __str__(self):
        if self.data_programada:
            return self.data_programada
        else:
            return str(self.id)

    class Meta:
        verbose_name = 'Programação do Recebimento do Cromograma'
        verbose_name_plural = 'Programações dos Recebimentos dos Cromogramas'
