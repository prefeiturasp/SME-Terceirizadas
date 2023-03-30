from django.db import models
from django.db.models import OuterRef
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField

from ...dados_comuns.behaviors import Logs, ModeloBase, TemIdentificadorExternoAmigavel
from ...dados_comuns.fluxo_status import CronogramaAlteracaoWorkflow, FluxoAlteracaoCronograma, FluxoCronograma
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
        if self.etapa and self.cronograma:
            return f'{self.etapa} do cronogrma {self.cronograma.numero}'
        if self.cronograma:
            return f'Etapa do cronogrma {self.cronograma.numero}'
        return 'Etapa sem cronograma'

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


class AlteracaoCronogramaEtapa(models.Model):
    etapa = models.ForeignKey(EtapasDoCronograma, on_delete=models.PROTECT)
    nova_data_programada = models.DateField('Nova Data Programada', blank=True, null=True)
    nova_quantidade = models.FloatField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.etapa.etapa} - {self.etapa.parte} (NovaQuantidade:{self.nova_quantidade})'


class SolicitacaoAlteracaoCronogramaQuerySet(models.QuerySet):
    def em_analise(self):
        return self.filter(status=CronogramaAlteracaoWorkflow.EM_ANALISE)

    def get_dashboard(self, status, filtros=None, init=None, end=None):
        log = LogSolicitacoesUsuario.objects.filter(uuid_original=OuterRef('uuid')).order_by(
            '-criado_em').values('criado_em')[:1]
        qs = self.filter(status__iexact=status).annotate(
            log_criado_em=log).order_by('-log_criado_em')
        if filtros:
            qs = self._filtrar_dashboard(qs, filtros)

        if init is not None and end is not None:
            return qs[init:end]
        return qs

    def _filtrar_dashboard(self, qs, filtros):
        if filtros:
            if 'nome_fornecedor' in filtros:
                qs = qs.filter(cronograma__empresa__nome_fantasia__icontains=filtros['nome_fornecedor'])
            if 'numero_cronograma' in filtros:
                qs = qs.filter(cronograma__numero__icontains=filtros['numero_cronograma'])

        return qs


class SolicitacaoAlteracaoCronograma(ModeloBase, TemIdentificadorExternoAmigavel, FluxoAlteracaoCronograma):
    MOTIVO_ALTERAR_DATA_ENTREGA = 'ALTERAR_DATA_ENTREGA'
    MOTIVO_ALTERAR_QTD_ALIMENTO = 'ALTERAR_QTD_ALIMENTO'
    MOTIVO_OUTROS = 'OUTROS'
    MOTIVO_NOMES = {
        MOTIVO_ALTERAR_DATA_ENTREGA: 'Alterar data de entrega',
        MOTIVO_ALTERAR_QTD_ALIMENTO: 'Alterar quantidade de alimento',
        MOTIVO_OUTROS: 'Outros',
    }

    MOTIVO_CHOICES = (
        (MOTIVO_ALTERAR_DATA_ENTREGA, MOTIVO_NOMES[MOTIVO_ALTERAR_DATA_ENTREGA]),
        (MOTIVO_ALTERAR_QTD_ALIMENTO, MOTIVO_NOMES[MOTIVO_ALTERAR_QTD_ALIMENTO]),
        (MOTIVO_OUTROS, MOTIVO_NOMES[MOTIVO_OUTROS]),
    )

    cronograma = models.ForeignKey(Cronograma, on_delete=models.PROTECT,
                                   related_name='solicitacoes_de_alteracao')

    etapas = models.ManyToManyField(AlteracaoCronogramaEtapa)

    motivo = MultiSelectField(choices=MOTIVO_CHOICES)
    justificativa = models.TextField('Justificativa de solicitação pelo fornecedor', blank=True)
    usuario_solicitante = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING)
    numero_solicitacao = models.CharField('Número da solicitação', blank=True, max_length=50, unique=True)

    objects = SolicitacaoAlteracaoCronogramaQuerySet.as_manager()

    def gerar_numero_solicitacao(self):
        self.numero_solicitacao = f'{str(self.pk).zfill(8)}-ALT'

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        log_transicao = LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.SOLICITACAO_DE_ALTERACAO_CRONOGRAMA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
        )
        return log_transicao

    def __str__(self):
        return f'Solicitação de alteração do cronograma: {self.numero_solicitacao}'

    class Meta:
        verbose_name = 'Solicitação de Alteração de Cronograma'
        verbose_name_plural = 'Solicitações de Alteração de Cronograma'


@receiver(post_save, sender=SolicitacaoAlteracaoCronograma)
def gerar_numero_solicitacao(sender, instance, created, **kwargs):
    if created:
        instance.gerar_numero_solicitacao()
        instance.save()
