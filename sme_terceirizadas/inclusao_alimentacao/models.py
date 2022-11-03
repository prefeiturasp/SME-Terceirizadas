from django.core.validators import MinValueValidator
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from ..dados_comuns.behaviors import (
    CriadoEm,
    CriadoPor,
    Descritivel,
    DiasSemana,
    IntervaloDeDia,
    Logs,
    Nomeavel,
    SolicitacaoForaDoPrazo,
    TemChaveExterna,
    TemData,
    TemIdentificadorExternoAmigavel,
    TemPrioridade,
    TemTerceirizadaConferiuGestaoAlimentacao
)
from ..dados_comuns.fluxo_status import FluxoAprovacaoPartindoDaEscola
from ..dados_comuns.models import LogSolicitacoesUsuario, TemplateMensagem
from .managers import (
    GrupoInclusoesDeAlimentacaoNormalDestaSemanaManager,
    GrupoInclusoesDeAlimentacaoNormalDesteMesManager,
    GrupoInclusoesDeAlimentacaoNormalVencidosDiasManager,
    InclusaoDeAlimentacaoCemeiDestaSemanaManager,
    InclusaoDeAlimentacaoCemeiDesteMesManager,
    InclusaoDeAlimentacaoDeCeiDestaSemanaManager,
    InclusaoDeAlimentacaoDeCeiDesteMesManager,
    InclusaoDeAlimentacaoDeCeiVencidosDiasManager,
    InclusoesDeAlimentacaoContinuaDestaSemanaManager,
    InclusoesDeAlimentacaoContinuaDesteMesManager,
    InclusoesDeAlimentacaoContinuaVencidaDiasManager
)


class QuantidadePorPeriodo(ExportModelOperationsMixin('quantidade_periodo'), DiasSemana, TemChaveExterna):
    numero_alunos = models.IntegerField(null=True, blank=True,)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao')
    observacao = models.CharField('Observação', blank=True, max_length=1000)
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


class MotivoInclusaoContinua(ExportModelOperationsMixin('motivo_inclusao_continua'), Nomeavel, TemChaveExterna):
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


class InclusaoAlimentacaoContinua(ExportModelOperationsMixin('inclusao_continua'), IntervaloDeDia, Descritivel,
                                  TemChaveExterna,
                                  FluxoAprovacaoPartindoDaEscola,
                                  CriadoPor, TemIdentificadorExternoAmigavel,
                                  CriadoEm, Logs, TemPrioridade, SolicitacaoForaDoPrazo,
                                  TemTerceirizadaConferiuGestaoAlimentacao):
    # TODO: noralizar campo de Descritivel: descricao -> observacao
    DESCRICAO = 'Inclusão de Alimentação Contínua'

    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=500)
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
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_CONTINUA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
        )

    def __str__(self):
        return f'de {self.data_inicial} até {self.data_final} para {self.escola}'

    class Meta:
        verbose_name = 'Inclusão de alimentação contínua'
        verbose_name_plural = 'Inclusões de alimentação contínua'
        ordering = ['data_inicial']


class MotivoInclusaoNormal(ExportModelOperationsMixin('motivo_inclusao_normal'), Nomeavel, TemChaveExterna):
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


class InclusaoAlimentacaoNormal(ExportModelOperationsMixin('inclusao_normal'), TemData, TemChaveExterna,
                                TemTerceirizadaConferiuGestaoAlimentacao):
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=500)
    cancelado = models.BooleanField('Esta cancelado?', default=False)
    cancelado_justificativa = models.CharField('Porque foi cancelado individualmente', blank=True, max_length=500)
    grupo_inclusao = models.ForeignKey('GrupoInclusaoAlimentacaoNormal',
                                       blank=True, null=True,
                                       on_delete=models.CASCADE,
                                       related_name='inclusoes_normais')

    def __str__(self):
        if self.outro_motivo:
            return f'Dia {self.data} - Outro motivo: {self.outro_motivo}'
        return f'Dia {self.data} {self.motivo}'

    class Meta:
        verbose_name = 'Inclusão de alimentação normal'
        verbose_name_plural = 'Inclusões de alimentação normal'
        ordering = ('data',)


class GrupoInclusaoAlimentacaoNormal(ExportModelOperationsMixin('grupo_inclusao'), Descritivel, TemChaveExterna,
                                     FluxoAprovacaoPartindoDaEscola, CriadoEm, SolicitacaoForaDoPrazo,
                                     CriadoPor, TemIdentificadorExternoAmigavel, Logs, TemPrioridade,
                                     TemTerceirizadaConferiuGestaoAlimentacao):
    DESCRICAO = 'Inclusão de Alimentação'

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
        return inclusao_normal.data if inclusao_normal else ''

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_NORMAL,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
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


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI(TemChaveExterna):
    inclusao_alimentacao_da_cei = models.ForeignKey('InclusaoAlimentacaoDaCEI',
                                                    blank=True, null=True,
                                                    on_delete=models.CASCADE,
                                                    related_name='quantidade_alunos_da_inclusao')
    faixa_etaria = models.ForeignKey('escola.FaixaEtaria', on_delete=models.DO_NOTHING)
    quantidade_alunos = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'De: {self.faixa_etaria.inicio} até: {self.faixa_etaria.fim} meses - {self.quantidade_alunos} alunos'

    class Meta:
        verbose_name = 'Quantidade de alunos por faixa etária da inclusao de alimentação'
        verbose_name_plural = 'Quantidade de alunos por faixa etária da inclusao de alimentação'


class InclusaoAlimentacaoDaCEI(Descritivel, TemData, TemChaveExterna, FluxoAprovacaoPartindoDaEscola, CriadoEm,
                               SolicitacaoForaDoPrazo, CriadoPor, TemIdentificadorExternoAmigavel, Logs, TemPrioridade,
                               TemTerceirizadaConferiuGestaoAlimentacao):
    DESCRICAO = 'Inclusão de Alimentação Por CEI'

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='grupos_inclusoes_por_cei')
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=500)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao')

    objects = models.Manager()  # Manager Padrão
    desta_semana = InclusaoDeAlimentacaoDeCeiDestaSemanaManager()
    deste_mes = InclusaoDeAlimentacaoDeCeiDesteMesManager()
    vencidos = InclusaoDeAlimentacaoDeCeiVencidosDiasManager()

    @property
    def quantidade_alunos_por_faixas_etarias(self):
        return self.quantidade_alunos_da_inclusao

    def adiciona_inclusao_a_quantidade_por_faixa_etaria(
        self, quantidade_por_faixa_etaria: QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI):  # noqa E128
        quantidade_por_faixa_etaria.inclusao_alimentacao_da_cei = self
        quantidade_por_faixa_etaria.save()

    @classmethod
    def get_solicitacoes_rascunho(cls, usuario):
        alimentacao_normal = cls.objects.filter(
            criado_por=usuario,
            status=InclusaoAlimentacaoDaCEI.workflow_class.RASCUNHO
        )
        return alimentacao_normal

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_CEI,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
        )

    def __str__(self):
        return f'Inclusao da CEI cód: {self.id_externo}'

    class Meta:
        verbose_name = 'Inclusão de alimentação da CEI'
        verbose_name_plural = 'Inclusões de alimentação da CEI'


class InclusaoDeAlimentacaoCEMEI(Descritivel, TemChaveExterna, FluxoAprovacaoPartindoDaEscola, CriadoEm, Logs,
                                 SolicitacaoForaDoPrazo, CriadoPor, TemIdentificadorExternoAmigavel, TemPrioridade,
                                 TemTerceirizadaConferiuGestaoAlimentacao):
    DESCRICAO = 'Inclusão de Alimentação CEMEI'

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='inclusoes_de_alimentacao_cemei')

    objects = models.Manager()  # Manager Padrão
    desta_semana = InclusaoDeAlimentacaoCemeiDestaSemanaManager()
    deste_mes = InclusaoDeAlimentacaoCemeiDesteMesManager()

    @property
    def data(self):
        dia_motivo = self.dias_motivos_da_inclusao_cemei.order_by('data').first()
        return dia_motivo.data if dia_motivo else ''

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_CEMEI,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
        )

    def __str__(self):
        return f'Inclusão de Alimentação CEMEI cód: {self.id_externo}'

    class Meta:
        verbose_name = 'Inclusão de alimentação CEMEI'
        verbose_name_plural = 'Inclusões de alimentação CEMEI'


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEI(TemChaveExterna):
    inclusao_alimentacao_cemei = models.ForeignKey('InclusaoDeAlimentacaoCEMEI',
                                                   on_delete=models.CASCADE,
                                                   related_name='quantidade_alunos_cei_da_inclusao_cemei')
    faixa_etaria = models.ForeignKey('escola.FaixaEtaria', on_delete=models.DO_NOTHING)
    quantidade_alunos = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    matriculados_quando_criado = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'De: {self.faixa_etaria.inicio} até: {self.faixa_etaria.fim} meses - {self.quantidade_alunos} alunos'

    class Meta:
        verbose_name = 'Quantidade de alunos por faixa etária da inclusao de alimentação CEMEI'
        verbose_name_plural = 'Quantidade de alunos por faixa etária da inclusao de alimentação CEMEI'


class QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEI(TemChaveExterna):
    inclusao_alimentacao_cemei = models.ForeignKey('InclusaoDeAlimentacaoCEMEI',
                                                   on_delete=models.CASCADE,
                                                   related_name='quantidade_alunos_emei_da_inclusao_cemei')
    quantidade_alunos = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    matriculados_quando_criado = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.periodo_escolar.nome} - {self.quantidade_alunos} alunos'

    class Meta:
        verbose_name = 'Quantidade de alunos EMEI por inclusao de alimentação CEMEI'
        verbose_name_plural = 'Quantidade de alunos EMEI por inclusao de alimentação CEMEI'


class DiasMotivosInclusaoDeAlimentacaoCEMEI(TemData, TemChaveExterna):
    inclusao_alimentacao_cemei = models.ForeignKey('InclusaoDeAlimentacaoCEMEI',
                                                   on_delete=models.CASCADE,
                                                   related_name='dias_motivos_da_inclusao_cemei')
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=500)
    cancelado = models.BooleanField('Esta cancelado?', default=False)
    cancelado_justificativa = models.CharField('Porque foi cancelado individualmente', blank=True, max_length=500)

    def __str__(self):
        if self.outro_motivo:
            return f'Dia {self.data} - Outro motivo: {self.outro_motivo}'
        return f'Dia {self.data} {self.motivo}'

    class Meta:
        verbose_name = 'Diaa e motivo inclusão de alimentação CEMEI'
        verbose_name_plural = 'Dias e motivos inclusçao de alimentação CEMEI'
        ordering = ('data',)
