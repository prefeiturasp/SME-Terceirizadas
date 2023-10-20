import os

from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import OuterRef
from django.db.models.signals import post_save
from django.dispatch import receiver

from ...dados_comuns.behaviors import (
    CriadoEm,
    Logs,
    ModeloBase,
    Nomeavel,
    TemChaveExterna,
    TemIdentificadorExternoAmigavel
)
from ...dados_comuns.fluxo_status import (
    CronogramaAlteracaoWorkflow,
    FluxoAlteracaoCronograma,
    FluxoCronograma,
    FluxoLayoutDeEmbalagem
)
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...dados_comuns.validators import validate_file_size_10mb
from ...produto.models import NomeDeProdutoEdital
from ...terceirizada.models import Contrato, Terceirizada


class UnidadeMedida(TemChaveExterna, Nomeavel, CriadoEm):
    abreviacao = models.CharField('Abreviação', max_length=25)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Unidade de Medida'
        verbose_name_plural = 'Unidades de Medida'
        unique_together = ('nome',)

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        self.abreviacao = self.abreviacao.lower()
        super().save(*args, **kwargs)


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


class SolicitacaoAlteracaoCronogramaQuerySet(models.QuerySet):
    def em_analise(self):
        return self.filter(status=CronogramaAlteracaoWorkflow.EM_ANALISE)

    def filtrar_por_status(self, status, filtros=None, init=None, end=None):
        log = LogSolicitacoesUsuario.objects.filter(uuid_original=OuterRef('uuid')).order_by(
            '-criado_em').values('criado_em')[:1]
        if not isinstance(status, list):
            status = [status]
        qs = self.filter(status__in=status).annotate(
            log_criado_em=log).order_by('-log_criado_em')
        if filtros:
            qs = self._filtrar_por_atributos_adicionais(qs, filtros)

        if init is not None and end is not None:
            return qs[init:end]
        return qs

    def _filtrar_por_atributos_adicionais(self, qs, filtros):
        if filtros:
            if 'nome_fornecedor' in filtros:
                qs = qs.filter(cronograma__empresa__nome_fantasia__icontains=filtros['nome_fornecedor'])
            if 'numero_cronograma' in filtros:
                qs = qs.filter(cronograma__numero__icontains=filtros['numero_cronograma'])
            if 'nome_produto' in filtros:
                qs = qs.filter(cronograma__produto__nome__icontains=filtros['nome_produto'])
        return qs


class SolicitacaoAlteracaoCronograma(ModeloBase, TemIdentificadorExternoAmigavel, FluxoAlteracaoCronograma, Logs):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.PROTECT,
                                   related_name='solicitacoes_de_alteracao')
    qtd_total_programada = models.FloatField('Qtd Total Programada', blank=True, null=True)
    etapas_antigas = models.ManyToManyField(EtapasDoCronograma, related_name='etapas_antigas')
    etapas_novas = models.ManyToManyField(EtapasDoCronograma, related_name='etapas_novas')
    programacoes_novas = models.ManyToManyField(
        ProgramacaoDoRecebimentoDoCronograma, related_name='programacoes_novas', blank=True)
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

    def cronograma_confirma_ciencia(self, justificativa, usuario, etapas, programacoes):
        from ..api.helpers import cria_etapas_de_cronograma, cria_programacao_de_cronograma

        self.etapas_novas.all().delete()
        etapas_criadas = cria_etapas_de_cronograma(etapas)
        self.etapas_novas.set(etapas_criadas)
        programacoes_criadas = cria_programacao_de_cronograma(programacoes)
        self.programacoes_novas.set(programacoes_criadas)
        self.cronograma_ciente(user=usuario, justificativa=justificativa)
        self.save()

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


class ImagemDoTipoDeEmbalagem(TemChaveExterna):
    tipo_de_embalagem = models.ForeignKey(
        'TipoDeEmbalagemDeLayout', on_delete=models.CASCADE, related_name='imagens', blank=True)
    arquivo = models.FileField(upload_to='layouts_de_embalagens', validators=[
        FileExtensionValidator(allowed_extensions=['PDF', 'PNG', 'JPG', 'JPEG']),
        validate_file_size_10mb])
    nome = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.tipo_de_embalagem.tipo_embalagem} - {self.nome}' if self.tipo_de_embalagem else str(self.id)

    def delete(self, *args, **kwargs):
        # Antes de excluir o objeto, exclui o arquivo associado
        if self.arquivo:
            if os.path.isfile(self.arquivo.path):
                os.remove(self.arquivo.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Imagem do Tipo de Embalagem'
        verbose_name_plural = 'Imagens dos Tipos de Embalagens'


class TipoDeEmbalagemDeLayout(TemChaveExterna):
    STATUS_APROVADO = 'APROVADO'
    STATUS_REPROVADO = 'REPROVADO'
    STATUS_EM_ANALISE = 'EM_ANALISE'
    TIPO_EMBALAGEM_PRIMARIA = 'PRIMARIA'
    TIPO_EMBALAGEM_SECUNDARIA = 'SECUNDARIA'
    TIPO_EMBALAGEM_TERCIARIA = 'TERCIARIA'

    STATUS_CHOICES = (
        (STATUS_APROVADO, 'Aprovado'),
        (STATUS_REPROVADO, 'Reprovado'),
        (STATUS_EM_ANALISE, 'Em análise'),
    )

    TIPO_EMBALAGEM_CHOICES = (
        (TIPO_EMBALAGEM_PRIMARIA, 'Primária'),
        (TIPO_EMBALAGEM_SECUNDARIA, 'Secundária'),
        (TIPO_EMBALAGEM_TERCIARIA, 'Terciária'),
    )

    layout_de_embalagem = models.ForeignKey(
        'LayoutDeEmbalagem', on_delete=models.CASCADE, blank=True, related_name='tipos_de_embalagens')
    tipo_embalagem = models.CharField(choices=TIPO_EMBALAGEM_CHOICES, max_length=10, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=STATUS_EM_ANALISE)
    complemento_do_status = models.TextField('Complemento do status', blank=True)

    def __str__(self):
        return f'{self.tipo_embalagem} - {self.status}' if self.tipo_embalagem else str(self.id)

    class Meta:
        verbose_name = 'Tipo de Embalagem de Layout'
        verbose_name_plural = 'Tipos de Embalagens de Layout'
        unique_together = ['layout_de_embalagem', 'tipo_embalagem']


class LayoutDeEmbalagem(ModeloBase, TemIdentificadorExternoAmigavel, Logs, FluxoLayoutDeEmbalagem):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.PROTECT, related_name='layouts')
    observacoes = models.TextField('Observações', blank=True)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.LAYOUT_DE_EMBALAGEM,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    @property
    def aprovado(self):
        return not self.tipos_de_embalagens.filter(status='REPROVADO').exists()

    @property
    def eh_primeira_analise(self):
        if self.log_mais_recente is not None:
            return not self.log_mais_recente.status_evento == LogSolicitacoesUsuario.LAYOUT_CORRECAO_REALIZADA

        return True

    def __str__(self):
        return f'{self.cronograma.numero} - {self.cronograma.produto.nome}' if self.cronograma else str(self.id)

    class Meta:
        verbose_name = 'Layout de Embalagem'
        verbose_name_plural = 'Layouts de Embalagem'
