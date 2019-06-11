import datetime
import pytest

from sme_pratoaberto_terceirizadas.alimentacao.models import InverterDiaCardapio

pytestmark = pytest.mark.django_db


def test_model_str_cardapio_inverter_dia_cardapio(cardapio, inverter_dia_cardapio):
    assert '{} - {}'.format(cardapio.data, cardapio.descricao) == cardapio.__str__()
    assert inverter_dia_cardapio.__str__() == inverter_dia_cardapio.uuid


def test_tipos_date_em_cardapio(cardapio):
    assert type(cardapio.data) == datetime.date
    assert type(cardapio.criado_em) == datetime.datetime


def test_tipo_user_em_cardapio(cardapio, user):
    assert type(cardapio.criado_por) == type(user)
    assert type(cardapio.atualizado_por) == type(user)


def test_str_inverter_dia_cardapio(inverter_dia_cardapio):
    assert inverter_dia_cardapio.__str__() == inverter_dia_cardapio.uuid


def test_tipo_data_de_e_data_para(inverter_dia_cardapio):
    assert type(inverter_dia_cardapio.data_de) == datetime.date
    assert type(inverter_dia_cardapio.data_para) == datetime.date


def test_tipos_usuario_escola(inverter_dia_cardapio, user, school):
    assert type(inverter_dia_cardapio.usuario) == type(user)
    assert type(inverter_dia_cardapio.escola) == type(school)


def test_validacao_final_semana(request_solicitar_errado, request_solicitar_certo):
    assert InverterDiaCardapio.valida_fim_semana(request_solicitar_errado) == False
    assert InverterDiaCardapio.valida_fim_semana(request_solicitar_certo) == True


def test_validacao_se_for_feriado(request_solicitar_feriado, request_solicitar_certo):
    assert not InverterDiaCardapio.valida_feriado(request_solicitar_feriado)
    assert InverterDiaCardapio.valida_feriado(request_solicitar_certo)
