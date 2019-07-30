from django.db import models

from ..dados_comuns.models_abstract import (
    Descritivel, TemData, TemChaveExterna, Ativavel,
    Nomeavel, CriadoEm, StatusValidacao, IntervaloDeDia,
    TemObservacao, FluxoAprovacaoPartindoDaEscola
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
    # TODO: adicionar fk para edital
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao)
    edital = models.ForeignKey('terceirizada.Edital', on_delete=models.DO_NOTHING)

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


class InversaoCardapio(CriadoEm, Descritivel, TemChaveExterna, StatusValidacao):
    """
        servir o cardápio do dia 30 no dia 15, automaticamente o
        cardápio do dia 15 será servido no dia 30
    """
    cardapio_de = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                    blank=True, null=True,
                                    related_name='cardapio_de')
    cardapio_para = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                      blank=True, null=True,
                                      related_name='cardapio_para')
    escola = models.ForeignKey('escola.Escola', blank=True, null=True,
                               on_delete=models.DO_NOTHING)

    def __str__(self):
        if self.cardapio_de and self.cardapio_para and self.escola:
            return '{}: \nDe: {} \nPara: {}'.format(self.escola.nome, self.cardapio_de, self.cardapio_para)
        return self.descricao

    class Meta:
        verbose_name = "Inversão de cardápio"
        verbose_name_plural = "Inversão de cardápios"


class SuspensaoAlimentacao(TemData, TemChaveExterna):
    """
        Uma escola pede para suspender as refeições:
        tipo pode ser cardapio, periodo (manha, tarde) ou itens do cardapio (Tipo alimentacao).

         - pode ser um cardapio inteiro
         - pode ser só um período(s) ( manhã, intermediário, tarde, vespertino, noturno, integral)
         - pode ser item(s) de um cardápio (Tipo alimentacao)
    """
    CARDAPIO_INTEIRO = 0
    PERIODO_ESCOLAR = 1
    TIPO_ALIMENTACAO = 2

    CHOICES = (
        (CARDAPIO_INTEIRO, 'Cardápio inteiro'),
        (PERIODO_ESCOLAR, 'Período escolar'),
        (TIPO_ALIMENTACAO, 'Tipo alimentação'),
    )

    # TODO: checar se criado_por é obrigatório ou opcional; caso seja obrigatório, remover blank e null ao resetar
    #  migrações (criar um novo initial)
    criado_por = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING, blank=True, null=True)
    tipo = models.PositiveSmallIntegerField(choices=CHOICES)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    cardapio = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    periodos_escolares = models.ManyToManyField('escola.PeriodoEscolar',
                                                blank=True)
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao,
                                               blank=True)

    @property
    def notificacao_enviar_para(self):
        # TODO: checar se quando cria uma notificação de um formulário, dispara para todos os usuários da DRE da Escola
        return self.escola.usuarios_diretoria_regional

    def __str__(self):
        return self.get_tipo_display()

    class Meta:
        verbose_name = "Suspensão de alimentação"
        verbose_name_plural = "Suspensões de alimentação"


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


class AlteracaoCardapio(CriadoEm, TemChaveExterna, IntervaloDeDia, TemObservacao, FluxoAprovacaoPartindoDaEscola):
    """
    A unidade quer trocar um ou mais tipos de refeição em um ou mais períodos escolares devido a um evento especial
    (motivo) em dado período de tempo.

    Ex: Alterar  nos períodos matutino e intermediario, o lanche e refeição pelo motivo "aniversariantes do mês"
    """

    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING, blank=True, null=True)
    motivo = models.ForeignKey('MotivoAlteracaoCardapio', on_delete=models.PROTECT, blank=True, null=True)

    @property
    def substituicoes(self):
        return self.substituicoes_periodo_escolar

    def __str__(self):
        return f'Alteração de cardápio: {self.uuid}'

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
