from django.db import models

from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Logs,
    Nomeavel,
    TemAno,
    TemChaveExterna,
    TemData,
    TemDia,
    TemIdentificadorExternoAmigavel,
    TemMes
)
from ..dados_comuns.fluxo_status import FluxoSolicitacaoMedicaoInicial, LogSolicitacoesUsuario
from ..escola.models import TipoUnidadeEscolar


class DiaSobremesaDoce(TemData, TemChaveExterna, CriadoEm, CriadoPor):
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar, on_delete=models.CASCADE)

    @property
    def tipo_unidades(self):
        return None

    def __str__(self):
        return f'{self.data.strftime("%d/%m/%Y")} - {self.tipo_unidade.iniciais}'

    class Meta:
        verbose_name = 'Dia de sobremesa doce'
        verbose_name_plural = 'Dias de sobremesa doce'
        unique_together = ('tipo_unidade', 'data',)
        ordering = ('data',)


class SolicitacaoMedicaoInicial(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    CriadoEm, CriadoPor,
    TemMes, TemAno,
    FluxoSolicitacaoMedicaoInicial,
    Logs,
):
    escola = models.ForeignKey('escola.Escola', on_delete=models.CASCADE,
                               related_name='solicitacoes_medicao_inicial')
    tipo_contagem_alimentacoes = models.ForeignKey('TipoContagemAlimentacao', on_delete=models.SET_NULL,
                                                   null=True, related_name='solicitacoes_medicao_inicial')
    com_ocorrencias = models.BooleanField('Com ocorrências?', default=False)
    ue_possui_alunos_periodo_parcial = models.BooleanField('Possui alunos periodo parcial?', default=False)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )

    @property
    def tem_ocorrencia(self):
        return hasattr(self, 'ocorrencia')

    class Meta:
        verbose_name = 'Solicitação de medição inicial'
        verbose_name_plural = 'Solicitações de medição inicial'
        unique_together = ('escola', 'mes', 'ano',)
        ordering = ('-ano', '-mes')

    def __str__(self):
        return f'Solicitação #{self.id_externo} -- Escola {self.escola.nome} -- {self.mes}/{self.ano}'


class OcorrenciaMedicaoInicial(TemChaveExterna, Logs, FluxoSolicitacaoMedicaoInicial):
    """Modelo para mapear a tabela Ocorrência e salvar objetos ocorrêcia da medição inicial."""

    nome_ultimo_arquivo = models.CharField(max_length=100)
    ultimo_arquivo = models.FileField()
    solicitacao_medicao_inicial = models.OneToOneField(
        SolicitacaoMedicaoInicial,
        on_delete=models.CASCADE,
        related_name='ocorrencia',
        blank=True, null=True
    )

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        log_transicao = LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            justificativa=justificativa,
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )
        return log_transicao

    def deletar_log_correcao(self, status_evento, **kwargs):
        LogSolicitacoesUsuario.objects.filter(
            descricao=str(self),
            status_evento__in=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            uuid_original=self.uuid,
        ).delete()

    def __str__(self):
        return f'Ocorrência {self.uuid} da Solicitação de Medição Inicial {self.solicitacao_medicao_inicial.uuid}'


class Responsavel(models.Model):
    nome = models.CharField('Nome', max_length=100)
    rf = models.CharField(max_length=10)
    solicitacao_medicao_inicial = models.ForeignKey(
        SolicitacaoMedicaoInicial,
        related_name='responsaveis',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Responsável {self.nome} - {self.rf}'


class TipoContagemAlimentacao(Nomeavel, TemChaveExterna, Ativavel):

    class Meta:
        verbose_name = 'Tipo de contagem das alimentações'
        verbose_name_plural = 'Tipos de contagem das alimentações'

    def __str__(self):
        return self.nome


class GrupoMedicao(Nomeavel, TemChaveExterna, Ativavel):

    class Meta:
        verbose_name = 'Grupo de medição'
        verbose_name_plural = 'Grupos de medição'

    def __str__(self):
        return self.nome


class Medicao(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    FluxoSolicitacaoMedicaoInicial,
    CriadoEm, CriadoPor, Logs
):
    solicitacao_medicao_inicial = models.ForeignKey('SolicitacaoMedicaoInicial', on_delete=models.CASCADE,
                                                    related_name='medicoes')
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', blank=True, null=True, on_delete=models.DO_NOTHING)
    grupo = models.ForeignKey(GrupoMedicao, blank=True, null=True, on_delete=models.PROTECT)
    alterado_em = models.DateTimeField('Alterado em', null=True, blank=True)

    def deletar_log_correcao(self, status_evento, **kwargs):
        LogSolicitacoesUsuario.objects.filter(
            descricao=str(self),
            status_evento__in=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            uuid_original=self.uuid,
        ).delete()

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            justificativa=justificativa,
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )

    @property
    def nome_periodo_grupo(self):
        if self.grupo and self.periodo_escolar:
            nome_periodo_grupo = f'{self.grupo.nome} - ' + f'{self.periodo_escolar.nome}'
        elif self.grupo and not self.periodo_escolar:
            nome_periodo_grupo = f'{self.grupo.nome}'
        else:
            nome_periodo_grupo = f'{self.periodo_escolar.nome}'
        return nome_periodo_grupo

    class Meta:
        verbose_name = 'Medição'
        verbose_name_plural = 'Medições'

    def __str__(self):
        ano = f'{self.solicitacao_medicao_inicial.ano}'
        mes = f'{self.solicitacao_medicao_inicial.mes}'

        return f'Medição #{self.id_externo} -- {self.nome_periodo_grupo} -- {mes}/{ano}'


class CategoriaMedicao(Nomeavel, Ativavel, TemChaveExterna):

    class Meta:
        verbose_name = 'Categoria de medição'
        verbose_name_plural = 'Categorias de medições'

    def __str__(self):
        return self.nome


class ValorMedicao(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    CriadoEm, TemDia
):
    valor = models.TextField('Valor do Campo')
    nome_campo = models.CharField(max_length=100)
    medicao = models.ForeignKey('Medicao', on_delete=models.CASCADE, related_name='valores_medicao')
    categoria_medicao = models.ForeignKey('CategoriaMedicao', on_delete=models.CASCADE,
                                          related_name='valores_medicao')
    tipo_alimentacao = models.ForeignKey('cardapio.TipoAlimentacao', blank=True,
                                         null=True, on_delete=models.DO_NOTHING)
    habilitado_correcao = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Valor da Medição'
        verbose_name_plural = 'Valores das Medições'

    def __str__(self):
        categoria = f'{self.categoria_medicao.nome}'
        nome_campo = f'{self.nome_campo}'
        dia = f'{self.dia}'
        mes = f'{self.medicao.solicitacao_medicao_inicial.mes}'
        return f'#{self.id_externo} -- Categoria {categoria} -- Campo {nome_campo} -- Dia/Mês {dia}/{mes}'
