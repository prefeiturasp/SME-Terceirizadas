import datetime

from django.core.validators import MinValueValidator
from django.db import models

from .managers import (
    InclusoesDeAlimentacaoContinuaPrazoLimiteDaquiA7DiasManager, InclusoesDeAlimentacaoContinuaPrazoLimiteManager,
    InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA30DiasManager,
    InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA7DiasManager, InclusoesDeAlimentacaoContinuaPrazoRegularManager,
    InclusoesDeAlimentacaoContinuaPrazoVencendoHojeManager, InclusoesDeAlimentacaoContinuaPrazoVencendoManager,
    InclusoesDeAlimentacaoContinuaVencidaDiasManager, InclusoesDeAlimentacaoNormalPrazoLimiteDaquiA7DiasManager,
    InclusoesDeAlimentacaoNormalPrazoLimiteManager, InclusoesDeAlimentacaoNormalPrazoRegularDaquiA30DiasManager,
    InclusoesDeAlimentacaoNormalPrazoRegularDaquiA7DiasManager, InclusoesDeAlimentacaoNormalPrazoRegularManager,
    InclusoesDeAlimentacaoNormalPrazoVencendoHojeManager, InclusoesDeAlimentacaoNormalPrazoVencendoManager,
    InclusoesDeAlimentacaoNormalVencidosDiasManager
)
from ..dados_comuns.constants import MINIMO_DIAS_PARA_PEDIDO, QUANTIDADE_DIAS_OK_PARA_PEDIDO
from ..dados_comuns.models import (
    LogSolicitacoesUsuario, TemplateMensagem
)
from ..dados_comuns.models_abstract import (
    CriadoEm, CriadoPor, Descritivel, DiasSemana, FluxoAprovacaoPartindoDaEscola, IntervaloDeDia, Logs, Nomeavel,
    TemChaveExterna, TemData, TemIdentificadorExternoAmigavel, TemPrioridade
)
from ..dados_comuns.utils import obter_dias_uteis_apos_hoje


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
        return "{} alunos para {} com {} tipo(s) de alimentação".format(
            self.numero_alunos, self.periodo_escolar,
            self.tipos_alimentacao.count())

    class Meta:
        verbose_name = "Quantidade por periodo"
        verbose_name_plural = "Quantidades por periodo"


class MotivoInclusaoContinua(Nomeavel, TemChaveExterna):
    """
        continuo -  mais educacao
        continuo-sp integral
        continuo - outro
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo de inclusao contínua"
        verbose_name_plural = "Motivos de inclusao contínua"


class InclusaoAlimentacaoContinua(IntervaloDeDia, Descritivel, TemChaveExterna,
                                  DiasSemana, FluxoAprovacaoPartindoDaEscola,
                                  CriadoPor, TemIdentificadorExternoAmigavel,
                                  CriadoEm, Logs, TemPrioridade):
    outro_motivo = models.CharField("Outro motivo", blank=True, max_length=50)
    motivo = models.ForeignKey(MotivoInclusaoContinua, on_delete=models.DO_NOTHING)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='inclusoes_alimentacao_continua')

    objects = models.Manager()  # Manager Padrão
    prazo_vencendo = InclusoesDeAlimentacaoContinuaPrazoVencendoManager()
    prazo_vencendo_hoje = InclusoesDeAlimentacaoContinuaPrazoVencendoHojeManager()
    prazo_limite = InclusoesDeAlimentacaoContinuaPrazoLimiteManager()
    prazo_limite_daqui_a_7_dias = InclusoesDeAlimentacaoContinuaPrazoLimiteDaquiA7DiasManager()
    prazo_regular = InclusoesDeAlimentacaoContinuaPrazoRegularManager()
    prazo_regular_daqui_a_7_dias = InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA7DiasManager()
    prazo_regular_daqui_a_30_dias = InclusoesDeAlimentacaoContinuaPrazoRegularDaquiA30DiasManager()
    vencidos = InclusoesDeAlimentacaoContinuaVencidaDiasManager()

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

    def salvar_log_transicao(self, status_evento, usuario):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_CONTINUA,
            usuario=usuario,
            uuid_original=self.uuid
        )

    def __str__(self):
        return f"de {self.data_inicial} até {self.data_final} para {self.escola} para {self.dias_semana_display()}"

    class Meta:
        verbose_name = "Inclusão de alimentação contínua"
        verbose_name_plural = "Inclusões de alimentação contínua"
        ordering = ['data_inicial']


class MotivoInclusaoNormal(Nomeavel, TemChaveExterna):
    """
        reposicao de aula
        dia de familia
        outro
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo de inclusao normal"
        verbose_name_plural = "Motivos de inclusao normais"


class InclusaoAlimentacaoNormal(TemData, TemChaveExterna, TemPrioridade):
    motivo = models.ForeignKey(MotivoInclusaoNormal, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField("Outro motivo", blank=True, max_length=50)
    grupo_inclusao = models.ForeignKey('GrupoInclusaoAlimentacaoNormal',
                                       blank=True, null=True,
                                       on_delete=models.CASCADE,
                                       related_name='inclusoes_normais')

    def __str__(self):
        if self.outro_motivo:
            return "Dia {} {} ".format(self.data, self.outro_motivo)
        return "Dia {} {} ".format(self.data, self.motivo)

    class Meta:
        verbose_name = "Inclusão de alimentação normal"
        verbose_name_plural = "Inclusões de alimentação normal"
        ordering = ('data',)


class GrupoInclusaoAlimentacaoNormal(Descritivel, TemChaveExterna, FluxoAprovacaoPartindoDaEscola,
                                     CriadoPor, TemIdentificadorExternoAmigavel, Logs, TemPrioridade):
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='grupos_inclusoes_normais')

    objects = models.Manager()  # Manager Padrão
    prazo_vencendo = InclusoesDeAlimentacaoNormalPrazoVencendoManager()
    prazo_vencendo_hoje = InclusoesDeAlimentacaoNormalPrazoVencendoHojeManager()
    prazo_limite = InclusoesDeAlimentacaoNormalPrazoLimiteManager()
    prazo_limite_daqui_a_7_dias = InclusoesDeAlimentacaoNormalPrazoLimiteDaquiA7DiasManager()
    prazo_regular = InclusoesDeAlimentacaoNormalPrazoRegularManager()
    prazo_regular_daqui_a_7_dias = InclusoesDeAlimentacaoNormalPrazoRegularDaquiA7DiasManager()
    prazo_regular_daqui_a_30_dias = InclusoesDeAlimentacaoNormalPrazoRegularDaquiA30DiasManager()
    vencidos = InclusoesDeAlimentacaoNormalVencidosDiasManager()

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
    def prioridade(self):
        """
            Dadas as inclusões normais, recupera a de menor data e retorna prioridade
        """
        descricao = ''
        prox_2_dias_uteis = obter_dias_uteis_apos_hoje(MINIMO_DIAS_PARA_PEDIDO)
        prox_3_dias_uteis = obter_dias_uteis_apos_hoje(3)
        prox_5_dias_uteis = obter_dias_uteis_apos_hoje(QUANTIDADE_DIAS_OK_PARA_PEDIDO)
        prox_6_dias_uteis = obter_dias_uteis_apos_hoje(6)
        hoje = datetime.date.today()

        inclusao_normal = self.inclusoes_normais.order_by('data').first()
        data = inclusao_normal.data

        if hoje <= data <= prox_2_dias_uteis:
            descricao = 'PRIORITARIO'
        elif prox_5_dias_uteis >= data >= prox_3_dias_uteis:
            descricao = 'LIMITE'
        elif data >= prox_6_dias_uteis:
            descricao = 'REGULAR'
        return descricao

    @property
    def descricao_curta(self):
        return f"Grupo de inclusão de alimentação normal #{self.id_externo}"

    def salvar_log_transicao(self, status_evento, usuario):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.INCLUSAO_ALIMENTACAO_NORMAL,
            usuario=usuario,
            uuid_original=self.uuid
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
        return "{} pedindo {} inclusoes".format(self.escola, self.inclusoes.count())

    class Meta:
        verbose_name = "Grupo de inclusão de alimentação normal"
        verbose_name_plural = "Grupos de inclusão de alimentação normal"
