import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy

from ...models import InversaoCardapio
from ....dados_comuns.constants import MINIMO_DIAS_PARA_PEDIDO, QUANTIDADE_DIAS_OK_PARA_PEDIDO
from ....dados_comuns.utils import obter_dias_uteis_apos_hoje

pytestmark = pytest.mark.django_db


def inversao_prazo_vencendo():
    cardapio_de = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(MINIMO_DIAS_PARA_PEDIDO))
    cardapio_para = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(420))
    escola = mommy.make('escola.Escola')
    inversao_cardapio_vencendo = mommy.make(InversaoCardapio,
                                            cardapio_de=cardapio_de,
                                            cardapio_para=cardapio_para,
                                            escola=escola)
    assert inversao_cardapio_vencendo in InversaoCardapio.prazo_vencendo.all()
    assert inversao_cardapio_vencendo not in InversaoCardapio.prazo_vencendo_hoje.all()


def inversao_prazo_vencendo_hoje():
    cardapio_de = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(420))
    cardapio_para = mommy.make('cardapio.Cardapio', data=datetime.date.today())
    escola = mommy.make('escola.Escola')
    inversao_cardapio_vencendo_hoje = mommy.make(InversaoCardapio,
                                                 cardapio_de=cardapio_de,
                                                 cardapio_para=cardapio_para,
                                                 escola=escola)
    assert inversao_cardapio_vencendo_hoje in InversaoCardapio.prazo_vencendo_hoje.all()
    assert inversao_cardapio_vencendo_hoje in InversaoCardapio.prazo_vencendo.all()


def inversao_prazo_limite_1():
    cardapio_de = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(QUANTIDADE_DIAS_OK_PARA_PEDIDO))
    cardapio_para = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(420))
    escola = mommy.make('escola.Escola')
    inversao_cardapio_prazo_limite = mommy.make(InversaoCardapio,
                                                cardapio_de=cardapio_de,
                                                cardapio_para=cardapio_para,
                                                escola=escola)
    assert inversao_cardapio_prazo_limite in InversaoCardapio.prazo_limite.all()


def inversao_prazo_limite_2():
    cardapio_de = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(MINIMO_DIAS_PARA_PEDIDO + 1))
    cardapio_para = mommy.make('cardapio.Cardapio', data=obter_dias_uteis_apos_hoje(420))
    escola = mommy.make('escola.Escola')
    inversao_cardapio_prazo_limite = mommy.make(InversaoCardapio,
                                                cardapio_de=cardapio_de,
                                                cardapio_para=cardapio_para,
                                                escola=escola)
    assert inversao_cardapio_prazo_limite in InversaoCardapio.prazo_limite.all()


@freeze_time("2019-12-30")
def test_segunda():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2019-12-31")
def test_terca():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2020-1-1")
def test_quarta():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2020-1-2")
def test_quinta():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2020-1-3")
def test_sexta():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2020-1-4")
def test_sabado():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()


@freeze_time("2020-1-5")
def test_domingo():
    inversao_prazo_limite_1()
    inversao_prazo_limite_2()
    inversao_prazo_vencendo_hoje()
    inversao_prazo_vencendo()
