import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy

from ..models import InclusaoAlimentacaoContinua
from ...dados_comuns.utils import obter_dias_uteis_apos_hoje

pytestmark = pytest.mark.django_db


def inclusao_continua_prazo_vencendo():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    assert inclusao_continua_hoje in InclusaoAlimentacaoContinua.prazo_vencendo.all()
    assert inclusao_continua_2_dias_uteis in InclusaoAlimentacaoContinua.prazo_vencendo.all()
    assert inclusao_continua_5_dias_uteis not in InclusaoAlimentacaoContinua.prazo_vencendo.all()
    assert inclusao_continua_20_dias_corridos not in InclusaoAlimentacaoContinua.prazo_vencendo.all()


def inclusao_continua_prazo_vencendo_hoje():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    assert inclusao_continua_hoje in InclusaoAlimentacaoContinua.prazo_vencendo_hoje.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_vencendo_hoje.all()
    assert inclusao_continua_5_dias_uteis not in InclusaoAlimentacaoContinua.prazo_vencendo_hoje.all()
    assert inclusao_continua_20_dias_corridos not in InclusaoAlimentacaoContinua.prazo_vencendo_hoje.all()


def inclusao_continua_prazo_limite():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_4_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(4))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    assert inclusao_continua_hoje not in InclusaoAlimentacaoContinua.prazo_limite.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_limite.all()
    assert inclusao_continua_4_dias_uteis in InclusaoAlimentacaoContinua.prazo_limite.all()
    assert inclusao_continua_5_dias_uteis not in InclusaoAlimentacaoContinua.prazo_limite.all()
    assert inclusao_continua_20_dias_corridos not in InclusaoAlimentacaoContinua.prazo_limite.all()


def inclusao_continua_prazo_limite_daqui_a_7_dias():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    assert inclusao_continua_hoje not in InclusaoAlimentacaoContinua.prazo_limite_daqui_a_7_dias.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_limite_daqui_a_7_dias.all()
    assert inclusao_continua_5_dias_uteis not in InclusaoAlimentacaoContinua.prazo_limite_daqui_a_7_dias.all()
    assert inclusao_continua_20_dias_corridos not in InclusaoAlimentacaoContinua.prazo_limite_daqui_a_7_dias.all()


def inclusao_continua_prazo_regular_daqui_a_30_dias():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    inclusao_continua_35_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=35))
    assert inclusao_continua_hoje not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias.all()
    assert inclusao_continua_5_dias_uteis in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias.all()
    assert inclusao_continua_20_dias_corridos in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias.all()
    assert inclusao_continua_35_dias_corridos not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias.all()


def inclusao_continua_prazo_regular_daqui_a_7_dias():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    inclusao_continua_35_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=35))
    assert inclusao_continua_hoje not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_7_dias.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_7_dias.all()
    assert inclusao_continua_20_dias_corridos not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_7_dias.all()
    assert inclusao_continua_35_dias_corridos not in InclusaoAlimentacaoContinua.prazo_regular_daqui_a_7_dias.all()


def inclusao_continua_prazo_regular():
    inclusao_continua_hoje = mommy.make(InclusaoAlimentacaoContinua, data_inicial=datetime.date.today())
    inclusao_continua_2_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(2))
    inclusao_continua_5_dias_uteis = mommy.make(InclusaoAlimentacaoContinua,
                                                data_inicial=obter_dias_uteis_apos_hoje(5))
    inclusao_continua_20_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    inclusao_continua_35_dias_corridos = mommy.make(InclusaoAlimentacaoContinua,
                                                    data_inicial=datetime.date.today() + datetime.timedelta(days=35))
    assert inclusao_continua_hoje not in InclusaoAlimentacaoContinua.prazo_regular.all()
    assert inclusao_continua_2_dias_uteis not in InclusaoAlimentacaoContinua.prazo_regular.all()
    assert inclusao_continua_5_dias_uteis in InclusaoAlimentacaoContinua.prazo_regular.all()
    assert inclusao_continua_20_dias_corridos in InclusaoAlimentacaoContinua.prazo_regular.all()
    assert inclusao_continua_35_dias_corridos in InclusaoAlimentacaoContinua.prazo_regular.all()


@freeze_time('2019-12-23')
def test_inclusao_continua_prazo_regular_segunda():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-24')
def test_inclusao_continua_prazo_regular_terca():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-25')
def test_inclusao_continua_prazo_regular_quarta():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-26')
def test_inclusao_continua_prazo_regular_quinta():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-27')
def test_inclusao_continua_prazo_regular_sexta():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-28')
def test_inclusao_continua_prazo_regular_sabado():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()


@freeze_time('2019-12-29')
def test_inclusao_continua_prazo_regular_domingo():
    inclusao_continua_prazo_regular()
    inclusao_continua_prazo_regular_daqui_a_7_dias()
    inclusao_continua_prazo_regular_daqui_a_30_dias()
    inclusao_continua_prazo_limite_daqui_a_7_dias()
    inclusao_continua_prazo_limite()
    inclusao_continua_prazo_vencendo_hoje()
    inclusao_continua_prazo_vencendo()
