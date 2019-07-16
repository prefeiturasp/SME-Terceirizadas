from django.db import models

from ..dados_comuns.models_abstract import (
    Descritivel, TemData, IntervaloDeDia,
    TemChaveExterna, Motivo, Ativavel, Nomeavel, CriadoEm, StatusValidacao
)
from ..escola.models import Escola, DiretoriaRegional


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


class AlteracaoCardapio(CriadoEm, Descritivel, TemChaveExterna):
    """
        Uma unidade quer alterar um tipo_alimentacao de cardápio de
        rotina para outro tipo_alimentacao de cardapio.
    """
    # TODO: colocar o controle de fluxo atraves do status
    # TODO: seria de tipoS de para tipoS para?
    tipo_de = models.ForeignKey(TipoAlimentacao, on_delete=models.DO_NOTHING,
                                blank=True, null=True,
                                related_name='tipo_de')
    tipo_para = models.ForeignKey(TipoAlimentacao, on_delete=models.DO_NOTHING,
                                  blank=True, null=True,
                                  related_name='tipo_para')
    escola = models.ForeignKey('escola.Escola', blank=True, null=True,
                               on_delete=models.DO_NOTHING)

    def __str__(self):
        if self.tipo_de and self.tipo_para and self.escola:
            return '{}: \nDe: {} \nPara: {}'.format(self.escola.nome, self.tipo_de, self.tipo_para)
        return self.descricao

    class Meta:
        verbose_name = "Alteração de cardápio"
        verbose_name_plural = "Alteração de cardápios"


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

    tipo = models.PositiveSmallIntegerField(choices=CHOICES)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    cardapio = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    periodos_escolares = models.ManyToManyField('escola.PeriodoEscolar',
                                                blank=True)
    tipos_alimentacao = models.ManyToManyField(TipoAlimentacao,
                                               blank=True)

    def __str__(self):
        return self.get_tipo_display()

    class Meta:
        verbose_name = "Suspensão de alimentação"
        verbose_name_plural = "Suspensões de alimentação"
