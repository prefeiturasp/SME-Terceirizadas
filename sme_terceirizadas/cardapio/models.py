from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from ..dados_comuns.behaviors import (  # noqa I101
    Ativavel,
    CriadoEm,
    CriadoPor,
    Descritivel,
    IntervaloDeDia,
    Logs,
    LogSolicitacoesUsuario,
    Motivo,
    Nomeavel,
    TemChaveExterna,
    TemData,
    TemIdentificadorExternoAmigavel,
    TemObservacao,
    TemPrioridade
)
from ..dados_comuns.fluxo_status import FluxoAprovacaoPartindoDaEscola, FluxoInformativoPartindoDaEscola
from ..dados_comuns.models import TemplateMensagem  # noqa I202
from .managers import (
    AlteracoesCardapioDestaSemanaManager,
    AlteracoesCardapioDesteMesManager,
    AlteracoesCardapioVencidaManager,
    GrupoSuspensaoAlimentacaoDestaSemanaManager,
    GrupoSuspensaoAlimentacaoDesteMesManager,
    InversaoCardapioDestaSemanaManager,
    InversaoCardapioDesteMesManager,
    InversaoCardapioVencidaManager
)


class TipoAlimentacao(ExportModelOperationsMixin('tipo_alimentacao'), Nomeavel, TemChaveExterna):
    """Compõe parte do cardápio.

    Dejejum
    Colação
    Almoço
    Refeição
    Sobremesa
    Lanche 4 horas
    Lanche 5 horas
    Lanche 6horas
    Merenda Seca
    """

    # TODO: tirar substituicoes quando der, não é mais necessário
    substituicoes = models.ManyToManyField('TipoAlimentacao', blank=True)

    @property
    def substituicoes_periodo_escolar(self):
        return self.substituicoes_periodo_escolar

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tipo de alimentação'
        verbose_name_plural = 'Tipos de alimentação'


class ComboDoVinculoTipoAlimentacaoPeriodoTipoUE(
    ExportModelOperationsMixin('substituicoes_vinculo_alimentacao'), TemChaveExterna):  # noqa E125

    tipos_alimentacao = models.ManyToManyField('TipoAlimentacao',
                                               related_name='%(app_label)s_%(class)s_possibilidades',
                                               help_text='Tipos de alimentacao do combo.',
                                               blank=True,
                                               )
    vinculo = models.ForeignKey('VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar',
                                null=True,
                                on_delete=models.CASCADE,
                                related_name='combos')

    def __str__(self):
        tipos_alimentacao_nome = [nome for nome in self.tipos_alimentacao.values_list('nome', flat=True)]
        return f'TiposAlim.:{tipos_alimentacao_nome}'

    class Meta:
        verbose_name = 'Combo do vínculo tipo alimentação'
        verbose_name_plural = 'Combos do vínculo tipo alimentação'


class SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE(TemChaveExterna):  # noqa E125

    tipos_alimentacao = models.ManyToManyField('TipoAlimentacao',
                                               related_name='%(app_label)s_%(class)s_possibilidades',
                                               help_text='Tipos de alimentacao das substituições dos combos.',
                                               blank=True,
                                               )
    combo = models.ForeignKey('ComboDoVinculoTipoAlimentacaoPeriodoTipoUE',
                              null=True,
                              on_delete=models.CASCADE,
                              related_name='substituicoes')

    def __str__(self):
        tipos_alimentacao_nome = [nome for nome in self.tipos_alimentacao.values_list('nome', flat=True)]
        return f'TiposAlim.:{tipos_alimentacao_nome}'

    class Meta:
        verbose_name = 'Substituição do combo do vínculo tipo alimentação'
        verbose_name_plural = 'Substituições do  combos do vínculo tipo alimentação'


class VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar(
    ExportModelOperationsMixin('vinculo_alimentacao_periodo_escolar_tipo_ue'), TemChaveExterna):  # noqa E125
    """Vincular vários tipos de alimentação a um periodo e tipo de U.E.

    Dado o tipo_unidade_escolar (EMEI, EMEF...) e
    em seguida o periodo_escolar(MANHA, TARDE..),
    trazer os tipos de alimentação que podem ser servidos.
    Ex.: Para CEI(creche) pela manhã (período) faz sentido ter mingau e não café da tarde.
    """

    tipo_unidade_escolar = models.ForeignKey('escola.TipoUnidadeEscolar',
                                             null=True,
                                             on_delete=models.DO_NOTHING)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar',
                                        null=True,
                                        on_delete=models.DO_NOTHING)

    def __str__(self):
        combos = [f'{str(sub)} --- ' for sub in self.combos.all()]
        return f'{self.tipo_unidade_escolar.iniciais} - {self.periodo_escolar.nome} - {combos}'

    class Meta:
        unique_together = [['periodo_escolar', 'tipo_unidade_escolar']]
        verbose_name = 'Vínculo tipo alimentação'
        verbose_name_plural = 'Vínculos tipo alimentação'


class Cardapio(ExportModelOperationsMixin('cardapio'), Descritivel, Ativavel, TemData, TemChaveExterna, CriadoEm):
    """Cardápio escolar.

    tem 1 data pra acontecer ex (26/06)
    tem 1 lista de tipos de alimentação (Dejejum, Colação, Almoço, LANCHE DE 4 HS OU 8 HS;
    LANCHE DE 5HS OU 6 HS; REFEIÇÃO).

    !!!OBS!!! PARA CEI varia por faixa de idade.
    """

    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao)
    edital = models.ForeignKey('terceirizada.Edital', on_delete=models.DO_NOTHING, related_name='editais')

    @property  # type: ignore
    def tipos_unidade_escolar(self):
        return self.tipos_unidade_escolar

    def __str__(self):
        if self.descricao:
            return f'{self.data}  - {self.descricao}'
        return f'{self.data}'

    class Meta:
        verbose_name = 'Cardápio'
        verbose_name_plural = 'Cardápios'


class InversaoCardapio(ExportModelOperationsMixin('inversao_cardapio'), CriadoEm, CriadoPor, TemObservacao, Motivo,
                       TemChaveExterna,
                       TemIdentificadorExternoAmigavel, FluxoAprovacaoPartindoDaEscola,
                       TemPrioridade, Logs):
    """Troca um cardápio de um dia por outro.

    servir o cardápio do dia 30 no dia 15, automaticamente o
    cardápio do dia 15 será servido no dia 30
    """

    objects = models.Manager()  # Manager Padrão
    desta_semana = InversaoCardapioDestaSemanaManager()
    deste_mes = InversaoCardapioDesteMesManager()
    vencidos = InversaoCardapioVencidaManager()

    cardapio_de = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                    blank=True, null=True,
                                    related_name='cardapio_de')
    cardapio_para = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                      blank=True, null=True,
                                      related_name='cardapio_para')
    escola = models.ForeignKey('escola.Escola', blank=True, null=True,
                               on_delete=models.DO_NOTHING)

    @classmethod
    def get_solicitacoes_rascunho(cls, usuario):
        solicitacoes_unificadas = InversaoCardapio.objects.filter(
            criado_por=usuario,
            status=InversaoCardapio.workflow_class.RASCUNHO
        )
        return solicitacoes_unificadas

    @property
    def data_de(self):
        return self.cardapio_de.data if self.cardapio_de else None

    @property
    def data_para(self):
        return self.cardapio_para.data if self.cardapio_para else None

    @property
    def data(self):
        return self.data_para if self.data_para < self.data_de else self.data_de 

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.INVERSAO_CARDAPIO)
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
            solicitacao_tipo=LogSolicitacoesUsuario.INVERSAO_DE_CARDAPIO,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    def __str__(self):
        return f'Inversão de \nDe: {self.cardapio_de} \nPara: {self.cardapio_para}'

    class Meta:
        verbose_name = 'Inversão de cardápio'
        verbose_name_plural = 'Inversão$ProjectFileDir$ de cardápios'


class MotivoSuspensao(ExportModelOperationsMixin('motivo_suspensao'), Nomeavel, TemChaveExterna):
    """Trabalha em conjunto com SuspensaoAlimentacao.

    Exemplos:
        - greve
        - reforma
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Motivo de suspensão de alimentação'
        verbose_name_plural = 'Motivo de suspensão de alimentação'


class SuspensaoAlimentacao(ExportModelOperationsMixin('suspensao_alimentacao'), TemData, TemChaveExterna):
    """Trabalha em conjunto com GrupoSuspensaoAlimentacao."""

    prioritario = models.BooleanField(default=False)
    motivo = models.ForeignKey(MotivoSuspensao, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField('Outro motivo', blank=True, max_length=50)
    grupo_suspensao = models.ForeignKey('GrupoSuspensaoAlimentacao', on_delete=models.CASCADE,
                                        blank=True, null=True, related_name='suspensoes_alimentacao')

    def __str__(self):
        return f'{self.motivo}'

    class Meta:
        verbose_name = 'Suspensão de alimentação'
        verbose_name_plural = 'Suspensões de alimentação'


class QuantidadePorPeriodoSuspensaoAlimentacao(ExportModelOperationsMixin('quantidade_periodo'), TemChaveExterna):
    numero_alunos = models.SmallIntegerField()
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    grupo_suspensao = models.ForeignKey('GrupoSuspensaoAlimentacao', on_delete=models.CASCADE,
                                        blank=True, null=True, related_name='quantidades_por_periodo')
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao)

    def __str__(self):
        return f'Quantidade de alunos: {self.numero_alunos}'

    class Meta:
        verbose_name = 'Quantidade por período de suspensão de alimentação'
        verbose_name_plural = 'Quantidade por período de suspensão de alimentação'


class GrupoSuspensaoAlimentacao(ExportModelOperationsMixin('grupo_suspensao_alimentacao'), TemChaveExterna, CriadoPor,
                                TemIdentificadorExternoAmigavel,
                                CriadoEm, TemObservacao, FluxoInformativoPartindoDaEscola, Logs,
                                TemPrioridade):
    """Serve para agrupar suspensões.

    Vide SuspensaoAlimentacao e QuantidadePorPeriodoSuspensaoAlimentacao
    """

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    objects = models.Manager()  # Manager Padrão
    desta_semana = GrupoSuspensaoAlimentacaoDestaSemanaManager()
    deste_mes = GrupoSuspensaoAlimentacaoDesteMesManager()

    @classmethod
    def get_informados(cls):
        return cls.objects.filter(
            status=cls.workflow_class.INFORMADO
        )

    @classmethod
    def get_tomados_ciencia(cls):
        return cls.objects.filter(
            status=cls.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA
        )

    @classmethod
    def get_rascunhos_do_usuario(cls, usuario):
        return cls.objects.filter(
            criado_por=usuario,
            status=cls.workflow_class.RASCUNHO
        )

    @property  # type: ignore
    def quantidades_por_periodo(self):
        return self.quantidades_por_periodo

    @property  # type: ignore
    def suspensoes_alimentacao(self):
        return self.suspensoes_alimentacao

    @property
    def data(self):
        query = self.suspensoes_alimentacao.order_by('data')
        return query.first().data

    def __str__(self):
        return f'{self.observacao}'

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.SUSPENSAO_ALIMENTACAO)
        template_troca = {  # noqa
            '@id': self.id,
            '@criado_em': str(self.criado_em),
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.SUSPENSAO_DE_CARDAPIO,
            usuario=usuario,
            uuid_original=self.uuid
        )

    class Meta:
        verbose_name = 'Grupo de suspensão de alimentação'
        verbose_name_plural = 'Grupo de suspensão de alimentação'


class SuspensaoAlimentacaoNoPeriodoEscolar(ExportModelOperationsMixin('suspensao_periodo_escolar'), TemChaveExterna):
    suspensao_alimentacao = models.ForeignKey(SuspensaoAlimentacao, on_delete=models.CASCADE,
                                              null=True, blank=True,
                                              related_name='suspensoes_periodo_escolar')
    qtd_alunos = models.PositiveSmallIntegerField(default=0)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.PROTECT,
                                        related_name='suspensoes_periodo_escolar')
    tipos_alimentacao = models.ManyToManyField('TipoAlimentacao', related_name='suspensoes_periodo_escolar')

    def __str__(self):
        return f'Suspensão de alimentação da Alteração de Cardápio: {self.suspensao_alimentacao}'

    class Meta:
        verbose_name = 'Suspensão de alimentação no período'
        verbose_name_plural = 'Suspensões de alimentação no período'


class MotivoAlteracaoCardapio(ExportModelOperationsMixin('motivo_alteracao_cardapio'), Nomeavel, TemChaveExterna):
    """Usado em conjunto com AlteracaoCardapio.

    Exemplos:
        - atividade diferenciada
        - aniversariante do mes
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Motivo de alteração de cardápio'
        verbose_name_plural = 'Motivos de alteração de cardápio'


class AlteracaoCardapio(ExportModelOperationsMixin('alteracao_cardapio'), CriadoEm, CriadoPor, TemChaveExterna,
                        IntervaloDeDia, TemObservacao,
                        FluxoAprovacaoPartindoDaEscola, TemIdentificadorExternoAmigavel, Logs,
                        TemPrioridade):
    objects = models.Manager()  # Manager Padrão
    desta_semana = AlteracoesCardapioDestaSemanaManager()
    deste_mes = AlteracoesCardapioDesteMesManager()
    vencidos = AlteracoesCardapioVencidaManager()

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING, blank=True, null=True)
    motivo = models.ForeignKey('MotivoAlteracaoCardapio', on_delete=models.PROTECT, blank=True, null=True)

    @property
    def data(self):
        data = self.data_inicial
        if self.data_final < data:
            data = self.data_final
        return data

    @property
    def substituicoes(self):
        return self.substituicoes_periodo_escolar

    def __str__(self):
        return f'Alteração de cardápio de: {self.data_inicial} para {self.data_final}'

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.ALTERACAO_CARDAPIO)
        template_troca = {  # noqa
            '@id': self.id,
            '@criado_em': str(self.criado_em),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.ALTERACAO_DE_CARDAPIO,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    class Meta:
        verbose_name = 'Alteração de cardápio'
        verbose_name_plural = 'Alterações de cardápio'


class SubstituicaoAlimentacaoNoPeriodoEscolar(ExportModelOperationsMixin('substituicao_alimentacao_periodo_escolar'),
                                              TemChaveExterna):
    alteracao_cardapio = models.ForeignKey('AlteracaoCardapio', on_delete=models.CASCADE,
                                           null=True, blank=True,
                                           related_name='substituicoes_periodo_escolar')
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.PROTECT,
                                        related_name='substituicoes_periodo_escolar')
    tipo_alimentacao_de = models.ForeignKey('cardapio.TipoAlimentacao', on_delete=models.PROTECT,
                                            related_name='substituicoes_tipo_alimentacao_de', blank=True, null=True)
    tipo_alimentacao_para = models.ForeignKey('cardapio.TipoAlimentacao', on_delete=models.PROTECT,
                                              related_name='substituicoes_tipo_alimentacao_para', blank=True, null=True)

    def __str__(self):
        return f'Substituições de alimentação: {self.uuid} da Alteração de Cardápio: {self.alteracao_cardapio.uuid}'

    class Meta:
        verbose_name = 'Substituições de alimentação no período'
        verbose_name_plural = 'Substituições de alimentação no período'
