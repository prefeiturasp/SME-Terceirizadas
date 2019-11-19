from django.core.validators import MinValueValidator
from django.db import models

from ..dados_comuns.behaviors import (
    CriadoEm,
    CriadoPor,
    Descritivel,
    DiasSemana,
    IntervaloDeDia,
    Logs,
    Nomeavel,
    TemChaveExterna,
    TemData,
    TemIdentificadorExternoAmigavel,
    TemPrioridade
)
from ..dados_comuns.fluxo_status import FluxoAprovacaoPartindoDaEscola
from ..dados_comuns.models import LogSolicitacoesUsuario, TemplateMensagem
from .managers import (
    GrupoInclusoesDeAlimentacaoNormalDestaSemanaManager,
    GrupoInclusoesDeAlimentacaoNormalDesteMesManager,
    GrupoInclusoesDeAlimentacaoNormalVencidosDiasManager,
    InclusoesDeAlimentacaoContinuaDestaSemanaManager,
    InclusoesDeAlimentacaoContinuaDesteMesManager,
    InclusoesDeAlimentacaoContinuaVencidaDiasManager
)


class QuantidadePorPeriodo(TemChaveExterna):
    numero_alunos = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao')
    grupo_inclusao_normal = models.ForeignKey('GrupoInclusaoAlimentacaoNormal',
                                              on_delete=models.CASCADE,
                                              null=True, blank=True,
                                              related_name='quantidades_por_periodo')
    inclusao_alimentacao_continua = models.ForeignKey('InclusaoAlimentacaoContinua',
                                                      on_delete=models.CASCADE,
                                                      null=True, blank=True,
                                                      related_name='quantidades_por_periodo')

    def __str__(self):
        qtd = self.tipos_alimentacao.count()
        return f'{self.numero_alunos} alunos para {self.periodo_escolar} com {qtd} tipo(s) de alimentação'


class Meta:
    verbose_name = 'Quantidade por periodo'
    verbose_name_plural = 'Quantidades por periodo'


class MotivoInclusaoContinua(Nomeavel, TemChaveExterna):
    """Funciona em conjunto com InclusaoAlimentacaoContinua.

    - continuo -  mais educacao
    - continuo-sp integral
    - continuo - outro
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Motivo de inclusao contínua'
        verbose_name_plural = 'Motivos de inclusao contínua'


class InclusaoAlimentacaoContinua(IntervaloDeDia, Descritivel, TemChaveExterna,
                                  DiasSemana, FluxoAprovacaoPartindoDaEscola,
                                  CriadoPor, TemIdentificadorExternoAmigavel,
                                  CriadoEm, Logs, TemPrioridade):
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=50)
    motivo = models.ForeignKey(MotivoInclusaoContinua, on_delete=models.DO_NOTHING)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='inclusoes_alimentacao_continua')

    objects = models.Manager()  # Manager Padrão
    desta_semana = InclusoesDeAlimentacaoContinuaDestaSemanaManager()
    deste_mes = InclusoesDeAlimentacaoContinuaDesteMesManager()
    vencidos = InclusoesDeAlimentacaoContinuaVencidaDiasManager()

    @property
    def data(self):
        data = self.data_inicial
        if self.data_final < data:
            data = self.data_final
        return data

    @classmethod
    def get_solicitacoes_rascunho(cls, usuario):
        inclusoes_continuas = cls.objects.filter(
            criado_por=usuario,
            status=InclusaoAlimentacaoContinua.workflow_class.RASCUNHO
        )
        return inclusoes_continuas

    @property
    def quantidades_periodo(self):
        return self.quantidades_por_periodo

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO_CONTINUA)
        template_troca = {
            '@id': self.id_externo,
            '@criado_em': str(self.criado_em),
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        for chave, valor in template_troca.items():
            corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_CONTINUA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    def __str__(self):
        return f'de {self.data_inicial} até {self.data_final} para {self.escola} para {self.dias_semana_display()}'

    class Meta:
        verbose_name = 'Inclusão de alimentação contínua'
        verbose_name_plural = 'Inclusões de alimentação contínua'
        ordering = ['data_inicial']


class MotivoInclusaoNormal(Nomeavel, TemChaveExterna):
    """Funciona em conjunto com InclusaoAlimentacaoNormal.

    - reposicao de aula
    - dia de familia
    - outro
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Motivo de inclusao normal'
        verbose_name_plural = 'Motivos de inclusao normais'


class InclusaoAlimentacaoNormal(TemData, TemChaveExterna):
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=50)
    grupo_inclusao = models.ForeignKey('GrupoInclusaoAlimentacaoNormal',
                                       blank=True, null=True,
                                       on_delete=models.CASCADE,
                                       related_name='inclusoes_normais')

    def __str__(self):
        if self.outro_motivo:
            return f'Dia {self.data} {self.outro_motivo}'
        return f'Dia {self.data} {self.motivo} '

    class Meta:
        verbose_name = 'Inclusão de alimentação normal'
        verbose_name_plural = 'Inclusões de alimentação normal'
        ordering = ('data',)


class GrupoInclusaoAlimentacaoNormal(Descritivel, TemChaveExterna, FluxoAprovacaoPartindoDaEscola, CriadoEm,
                                     CriadoPor, TemIdentificadorExternoAmigavel, Logs, TemPrioridade):
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='grupos_inclusoes_normais')

    objects = models.Manager()  # Manager Padrão
    desta_semana = GrupoInclusoesDeAlimentacaoNormalDestaSemanaManager()
    deste_mes = GrupoInclusoesDeAlimentacaoNormalDesteMesManager()
    vencidos = GrupoInclusoesDeAlimentacaoNormalVencidosDiasManager()

    @classmethod
    def get_solicitacoes_rascunho(cls, usuario):
        alimentacao_normal = cls.objects.filter(
            criado_por=usuario,
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.RASCUNHO
        )
        return alimentacao_normal

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO)
        template_troca = {
            '@id': self.id_externo,
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        for chave, valor in template_troca.items():
            corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    @property
    def data(self):
        inclusao_normal = self.inclusoes_normais.order_by('data').first()
        return inclusao_normal.data

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_NORMAL,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    @property
    def inclusoes(self):
        return self.inclusoes_normais

    @property
    def quantidades_periodo(self):
        return self.quantidades_por_periodo

    def adiciona_inclusao_normal(self, inclusao: InclusaoAlimentacaoNormal):
        # TODO: padronizar grupo_inclusao ou grupo_inclusao_normal
        inclusao.grupo_inclusao = self
        inclusao.save()

    def adiciona_quantidade_periodo(self, quantidade_periodo: QuantidadePorPeriodo):
        # TODO: padronizar grupo_inclusao ou grupo_inclusao_normal
        quantidade_periodo.grupo_inclusao_normal = self
        quantidade_periodo.save()

    def __str__(self):
        return f'{self.escola} pedindo {self.inclusoes.count()} inclusoes'

    class Meta:
        verbose_name = 'Grupo de inclusão de alimentação normal'
        verbose_name_plural = 'Grupos de inclusão de alimentação normal'
