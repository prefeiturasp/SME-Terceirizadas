import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy

from ..models import AlteracaoCardapio, InversaoCardapio

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-4')
def test_manager_inversao_vencida(datas_inversao_vencida):
    dia_de, dia_para, status = datas_inversao_vencida

    cardapio_de = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_de))
    cardapio_para = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_para))
    inversao_cardapio_vencida = mommy.make(InversaoCardapio,
                                           cardapio_de=cardapio_de,
                                           cardapio_para=cardapio_para,
                                           status=status)
    assert inversao_cardapio_vencida in InversaoCardapio.vencidos.all()
    assert inversao_cardapio_vencida not in InversaoCardapio.desta_semana.all()
    assert inversao_cardapio_vencida not in InversaoCardapio.deste_mes.all()


@freeze_time('2019-10-4')
def test_manager_inversao_desta_semana(datas_inversao_desta_semana):
    dia_de, dia_para, status = datas_inversao_desta_semana

    cardapio_de = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_de))
    cardapio_para = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_para))
    inversao_cardapio_desta_semana = mommy.make(InversaoCardapio,
                                                cardapio_de=cardapio_de,
                                                cardapio_para=cardapio_para,
                                                status=status)
    assert inversao_cardapio_desta_semana in InversaoCardapio.desta_semana.all()
    assert inversao_cardapio_desta_semana in InversaoCardapio.deste_mes.all()
    assert inversao_cardapio_desta_semana not in InversaoCardapio.vencidos.all()


@freeze_time('2019-10-4')
def test_manager_inversao_deste_mes(datas_inversao_deste_mes):
    dia_de, dia_para, status = datas_inversao_deste_mes

    cardapio_de = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_de))
    cardapio_para = mommy.make('cardapio.Cardapio', data=datetime.date(*dia_para))
    inversao_cardapio_desta_semana = mommy.make(InversaoCardapio,
                                                cardapio_de=cardapio_de,
                                                cardapio_para=cardapio_para,
                                                status=status)
    assert inversao_cardapio_desta_semana in InversaoCardapio.deste_mes.all()
    assert inversao_cardapio_desta_semana not in InversaoCardapio.vencidos.all()


@freeze_time('2019-10-4')
def test_manager_altercao_vencida(datas_alteracao_vencida):
    data_inicial, status = datas_alteracao_vencida

    data_inicial = datetime.date(*data_inicial)
    data_final = data_inicial + datetime.timedelta(days=10)
    alteracao_cardapio_vencida = mommy.make(AlteracaoCardapio,
                                            data_inicial=data_inicial,
                                            data_final=data_final,
                                            status=status)
    assert alteracao_cardapio_vencida in AlteracaoCardapio.vencidos.all()
    assert alteracao_cardapio_vencida not in AlteracaoCardapio.desta_semana.all()
    assert alteracao_cardapio_vencida not in AlteracaoCardapio.deste_mes.all()


@freeze_time('2019-10-4')
def test_manager_alteracao_desta_semana(datas_alteracao_semana):
    data_inicial, status = datas_alteracao_semana

    data_inicial = datetime.date(*data_inicial)
    data_final = data_inicial + datetime.timedelta(days=10)
    alteracao_cardapio_semana = mommy.make(AlteracaoCardapio,
                                           data_inicial=data_inicial,
                                           data_final=data_final,
                                           status=status)
    assert alteracao_cardapio_semana not in AlteracaoCardapio.vencidos.all()
    assert alteracao_cardapio_semana in AlteracaoCardapio.desta_semana.all()
    assert alteracao_cardapio_semana in AlteracaoCardapio.deste_mes.all()


@freeze_time('2019-10-4')
def test_manager_alteracao_deste_mes(datas_alteracao_mes):
    data_inicial, status = datas_alteracao_mes

    data_inicial = datetime.date(*data_inicial)
    data_final = data_inicial + datetime.timedelta(days=10)
    alteracao_cardapio_mes = mommy.make(AlteracaoCardapio,
                                        data_inicial=data_inicial,
                                        data_final=data_final,
                                        status=status)
    assert alteracao_cardapio_mes not in AlteracaoCardapio.vencidos.all()
    assert alteracao_cardapio_mes in AlteracaoCardapio.deste_mes.all()
