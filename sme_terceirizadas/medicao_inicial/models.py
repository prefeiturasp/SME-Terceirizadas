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

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )

    class Meta:
        verbose_name = 'Solicitação de medição inicial'
        verbose_name_plural = 'Solicitações de medição inicial'
        unique_together = ('escola', 'mes', 'ano',)
        ordering = ('-criado_em',)

    def __str__(self):
        return f'Solicitação #{self.id_externo} -- Escola {self.escola.nome} -- {self.mes}/{self.ano}'


class AnexoOcorrenciaMedicaoInicial(TemChaveExterna):
    nome = models.CharField(max_length=100)
    arquivo = models.FileField()
    solicitacao_medicao_inicial = models.OneToOneField(
        SolicitacaoMedicaoInicial,
        related_name='anexo',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Anexo Ocorrência {self.uuid} - {self.nome}'


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
