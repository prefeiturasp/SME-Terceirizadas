import datetime

from django.db import models

from .managers import (
    AlteracoesCardapioPrazoVencendoManager,
    AlteracoesCardapioPrazoLimiteManager,
    AlteracoesCardapioPrazoRegularManager,
    AlteracoesCardapioPrazoVencendoHojeManager,
    AlteracoesCardapioPrazoLimiteDaquiA7DiasManager,
    AlteracoesCardapioPrazoRegularDaquiA7DiasManager,
    AlteracoesCardapioPrazoRegularDaquiA30DiasManager
)
from .managers import (
    AlteracoesCardapioVencidaManager,
    InversaoCardapioVencidaManager
)
from ..dados_comuns.models import TemplateMensagem
from ..dados_comuns.models_abstract import (
    Descritivel, TemData, TemChaveExterna, Ativavel,
    Nomeavel, CriadoEm, IntervaloDeDia, CriadoPor,
    TemObservacao, FluxoAprovacaoPartindoDaEscola,
    Motivo, Logs, LogSolicitacoesUsuario,
    TemIdentificadorExternoAmigavel,
    FluxoInformativoPartindoDaEscola, FluxoInformativoPartindoDaEscola
)


class TipoAlimentacao(Nomeavel, TemChaveExterna):
    """
        Dejejum
        Colação
        Almoço
        Refeição
        sobremesa
        Lanche 4 horas
        Lanche 5 horas
        Lanche 6horas
        Merenda Seca
    """

    @property
    def substituicoes_periodo_escolar(self):
        return self.substituicoes_periodo_escolar

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de alimentação"
        verbose_name_plural = "Tipos de alimentação"


class Cardapio(Descritivel, Ativavel, TemData, TemChaveExterna, CriadoEm):
    """
        Cardápio escolar tem:
        tem 1 data pra acontecer ex (26/06)
        tem 1 lista de tipos de alimentação (Dejejum, Colação, Almoço, LANCHE DE 4 HS OU 8 HS;
            LANCHE DE 5HS OU 6 HS; REFEIÇÃO).

        !!!OBS!!! PARA CEI varia por faixa de idade.
    """
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao)
    edital = models.ForeignKey('terceirizada.Edital', on_delete=models.DO_NOTHING, related_name='editais')

    @property
    def tipos_unidade_escolar(self):
        return self.tipos_unidade_escolar

    def __str__(self):
        if self.descricao:
            return '{}  - {}'.format(self.data, self.descricao)
        return '{}'.format(self.data)

    class Meta:
        verbose_name = "Cardápio"
        verbose_name_plural = "Cardápios"


class InversaoCardapio(CriadoEm, CriadoPor, TemObservacao, Motivo, TemChaveExterna,
                       TemIdentificadorExternoAmigavel, FluxoAprovacaoPartindoDaEscola):
    """
        servir o cardápio do dia 30 no dia 15, automaticamente o
        cardápio do dia 15 será servido no dia 30
    """

    objects = models.Manager()  # Manager Padrão
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
    def descricao_curta(self):
        return f"Inversão de dia de Cardápio #{self.id_externo}"

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

    def salvar_log_transicao(self, status_evento, usuario):
        pass

    def __str__(self):
        if self.cardapio_de and self.cardapio_para and self.escola:
            return '{}: \nDe: {} \nPara: {}'.format(self.escola.nome, self.cardapio_de, self.cardapio_para)
        return self.descricao

    class Meta:
        verbose_name = "Inversão de cardápio"
        verbose_name_plural = "Inversão de cardápios"


class MotivoSuspensao(Nomeavel, TemChaveExterna):
    """
    Exemplos:
        - greve
        - reforma
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo de suspensão de alimentação"
        verbose_name_plural = "Motivo de suspensão de alimentação"


class SuspensaoAlimentacao(TemData, TemChaveExterna):
    """
    Uma escola pede para suspender as refeições: escolhe os
    """
    prioritario = models.BooleanField(default=False)
    motivo = models.ForeignKey(MotivoSuspensao, on_delete=models.DO_NOTHING)
    outro_motivo = models.CharField("Outro motivo", blank=True, null=True, max_length=50)
    grupo_suspensao = models.ForeignKey('GrupoSuspensaoAlimentacao', on_delete=models.CASCADE,
                                        blank=True, null=True, related_name='suspensoes_alimentacao')

    def __str__(self):
        return f"{self.motivo}"

    class Meta:
        verbose_name = "Suspensão de alimentação"
        verbose_name_plural = "Suspensões de alimentação"


class QuantidadePorPeriodoSuspensaoAlimentacao(TemChaveExterna):
    numero_alunos = models.SmallIntegerField()
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.DO_NOTHING)
    grupo_suspensao = models.ForeignKey('GrupoSuspensaoAlimentacao', on_delete=models.CASCADE,
                                        blank=True, null=True, related_name='quantidades_por_periodo')
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao)

    def __str__(self):
        return f"Quantidade de alunos: {self.numero_alunos}"

    class Meta:
        verbose_name = "Quantidade por período de suspensão de alimentação"
        verbose_name_plural = "Quantidade por período de suspensão de alimentação"


class GrupoSuspensaoAlimentacao(TemChaveExterna, CriadoPor, TemIdentificadorExternoAmigavel,
                                CriadoEm, TemObservacao, FluxoInformativoPartindoDaEscola):
    """
        Serve para agrupar suspensões
    """
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)

    @classmethod
    def get_rascunhos_do_usuario(cls, usuario):
        return cls.objects.filter(
            criado_por=usuario,
            status=cls.workflow_class.RASCUNHO
        )

    @property
    def quantidades_por_periodo(self):
        return self.quantidades_por_periodo

    @property
    def suspensoes_alimentacao(self):
        return self.suspensoes_alimentacao

    def __str__(self):
        return f"{self.observacao}"

    @property
    def descricao_curta(self):
        return "Suspensão de Alimentação."

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.SUSPENSAO_ALIMENTACAO)
        template_troca = {
            '@id': self.id,
            '@criado_em': str(self.criado_em),
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        # for chave, valor in template_troca.items():
        #     corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario):
        pass

    class Meta:
        verbose_name = "Grupo de suspensão de alimentação"
        verbose_name_plural = "Grupo de suspensão de alimentação"


class SuspensaoAlimentacaoNoPeriodoEscolar(TemChaveExterna):
    suspensao_alimentacao = models.ForeignKey(SuspensaoAlimentacao, on_delete=models.CASCADE,
                                              null=True, blank=True,
                                              related_name="suspensoes_periodo_escolar")
    qtd_alunos = models.PositiveSmallIntegerField(default=0)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.PROTECT,
                                        related_name="suspensoes_periodo_escolar")
    tipos_alimentacao = models.ManyToManyField('TipoAlimentacao', related_name="suspensoes_periodo_escolar")

    def __str__(self):
        return f'Suspensão de alimentação da Alteração de Cardápio: {self.suspensao_alimentacao}'

    class Meta:
        verbose_name = "Suspensão de alimentação no período"
        verbose_name_plural = "Suspensões de alimentação no período"


class MotivoAlteracaoCardapio(Nomeavel, TemChaveExterna):
    """
    Exemplos:
        - atividade diferenciada
        - aniversariante do mes
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo de alteração de cardápio"
        verbose_name_plural = "Motivos de alteração de cardápio"


class AlteracaoCardapio(CriadoEm, TemChaveExterna, IntervaloDeDia, TemObservacao,
                        FluxoAprovacaoPartindoDaEscola, TemIdentificadorExternoAmigavel, Logs):
    """
    A unidade quer trocar um ou mais tipos de refeição em um ou mais períodos escolares devido a um evento especial
    (motivo) em dado período de tempo.

    Ex: Alterar  nos períodos matutino e intermediario, o lanche e refeição pelo motivo "aniversariantes do mês"
    """

    objects = models.Manager()  # Manager Padrão
    prazo_vencendo = AlteracoesCardapioPrazoVencendoManager()
    prazo_vencendo_hoje = AlteracoesCardapioPrazoVencendoHojeManager()

    prazo_limite = AlteracoesCardapioPrazoLimiteManager()
    prazo_limite_daqui_a_7_dias = AlteracoesCardapioPrazoLimiteDaquiA7DiasManager()

    prazo_regular = AlteracoesCardapioPrazoRegularManager()
    prazo_regular_daqui_a_7_dias = AlteracoesCardapioPrazoRegularDaquiA7DiasManager()
    prazo_regular_daqui_a_30_dias = AlteracoesCardapioPrazoRegularDaquiA30DiasManager()
    vencidos = AlteracoesCardapioVencidaManager()

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING, blank=True, null=True)
    motivo = models.ForeignKey('MotivoAlteracaoCardapio', on_delete=models.PROTECT, blank=True, null=True)

    @property
    def substituicoes(self):
        return self.substituicoes_periodo_escolar

    def __str__(self):
        return f'Alteração de cardápio: {self.uuid}'

    @property
    def descricao_curta(self):
        return "Solicitação de alteração de cardápio."

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.ALTERACAO_CARDAPIO)
        template_troca = {
            '@id': self.id,
            '@criado_em': str(self.criado_em),
            # '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        # for chave, valor in template_troca.items():
        #     corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.ALTERACAO_DE_CARDAPIO,
            usuario=usuario,
            uuid_original=self.uuid
        )

    @classmethod
    def solicitacoes_por_visao(cls, query_set_base, visao):
        if visao == "dia":
            query_set_por_visao = query_set_base \
                .filter(data_inicial__lte=datetime.datetime.today(), data_final__gte=datetime.datetime.today())

        elif visao == "semana":
            query_set_por_visao = query_set_base \
                .filter(data_inicial__gte=datetime.datetime.today() + datetime.timedelta(days=7),
                        data_final__lte=datetime.datetime.today() + datetime.timedelta(days=7))

        elif visao == "mes":
            query_set_por_visao = query_set_base \
                .filter(data_inicial__gte=datetime.datetime.today() + datetime.timedelta(days=30),
                        data_final__lte=datetime.datetime.today() + datetime.timedelta(days=30))

        else:
            query_set_por_visao = AlteracaoCardapio.objects.none()

        return query_set_por_visao

    @classmethod
    def solicitacoes_vencendo_por_usuario_e_visao(cls, usuario, visao):
        query_set_base = AlteracaoCardapio.prazo_vencendo.filter(escola__diretoria_regional__usuarios=usuario)
        query_set_por_visao = AlteracaoCardapio.solicitacoes_por_visao(query_set_base, visao)

        return query_set_por_visao

    @classmethod
    def solicitacoes_limite_por_usuario_e_visao(cls, usuario, visao):
        query_set_base = AlteracaoCardapio.prazo_limite.filter(escola__diretoria_regional__usuarios=usuario)

        query_set_por_visao = AlteracaoCardapio.solicitacoes_por_visao(query_set_base, visao)

        return query_set_por_visao

    @classmethod
    def solicitacoes_regulares_por_usuario_e_visao(cls, usuario, visao):
        query_set_base = AlteracaoCardapio.prazo_regular.filter(escola__diretoria_regional__usuarios=usuario)

        query_set_por_visao = AlteracaoCardapio.solicitacoes_por_visao(query_set_base, visao)

        return query_set_por_visao

    class Meta:
        verbose_name = "Alteração de cardápio"
        verbose_name_plural = "Alterações de cardápio"


class SubstituicoesAlimentacaoNoPeriodoEscolar(TemChaveExterna):
    alteracao_cardapio = models.ForeignKey('AlteracaoCardapio', on_delete=models.CASCADE,
                                           null=True, blank=True,
                                           related_name="substituicoes_periodo_escolar")
    qtd_alunos = models.PositiveSmallIntegerField(default=0)
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', on_delete=models.PROTECT,
                                        related_name="substituicoes_periodo_escolar")
    tipos_alimentacao = models.ManyToManyField('TipoAlimentacao', related_name="substituicoes_periodo_escolar")

    def __str__(self):
        return f'Substituições de alimentação: {self.uuid} da Alteração de Cardápio: {self.alteracao_cardapio.uuid}'

    class Meta:
        verbose_name = "Substituições de alimentação no período"
        verbose_name_plural = "Substituições de alimentação no período"
