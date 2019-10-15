import pytest
from freezegun import freeze_time
from model_mommy import mommy

from ..models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua, InclusaoAlimentacaoNormal

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-4')
def test_manager_inclusao_continua_desta_semana(inclusao_alimentacao_continua_parametros_semana):
    data_inicial, data_final = inclusao_alimentacao_continua_parametros_semana

    inclusao_continua = mommy.make(InclusaoAlimentacaoContinua,
                                   data_inicial=data_inicial,
                                   data_final=data_final)
    assert inclusao_continua in InclusaoAlimentacaoContinua.desta_semana.all()


@freeze_time('2019-10-4')
def test_manager_inclusao_continua_deste_mes(inclusao_alimentacao_continua_parametros_mes):
    data_inicial, data_final = inclusao_alimentacao_continua_parametros_mes

    inclusao_continua = mommy.make(InclusaoAlimentacaoContinua,
                                   data_inicial=data_inicial,
                                   data_final=data_final)
    assert inclusao_continua in InclusaoAlimentacaoContinua.deste_mes.all()


@freeze_time('2019-10-4')
def test_manager_inclusao_continua_vencidos(inclusao_alimentacao_continua_parametros_vencidos):
    data_inicial, data_final, status = inclusao_alimentacao_continua_parametros_vencidos

    inclusao_continua = mommy.make(InclusaoAlimentacaoContinua,
                                   data_inicial=data_inicial,
                                   data_final=data_final,
                                   status=status)
    assert inclusao_continua in InclusaoAlimentacaoContinua.vencidos.all()


@freeze_time('2019-10-4')
def test_manager_inclusoes_normais_desta_semana(inclusao_alimentacao_continua_parametros_semana):
    data_evento, _ = inclusao_alimentacao_continua_parametros_semana

    grupo_inclusoes = mommy.make(GrupoInclusaoAlimentacaoNormal)
    mommy.make(InclusaoAlimentacaoNormal, data=data_evento,
               grupo_inclusao=grupo_inclusoes)
    assert grupo_inclusoes in GrupoInclusaoAlimentacaoNormal.desta_semana.all()


@freeze_time('2019-10-4')
def test_manager_inclusoes_normais_deste_mes(inclusao_alimentacao_continua_parametros_mes):
    data_evento, _ = inclusao_alimentacao_continua_parametros_mes

    grupo_inclusoes = mommy.make(GrupoInclusaoAlimentacaoNormal)
    mommy.make(InclusaoAlimentacaoNormal, data=data_evento,
               grupo_inclusao=grupo_inclusoes)
    assert grupo_inclusoes in GrupoInclusaoAlimentacaoNormal.deste_mes.all()


@freeze_time('2019-10-4')
def test_manager_inclusoes_normais_vencidos(inclusao_alimentacao_continua_parametros_vencidos):
    data_evento, _, status = inclusao_alimentacao_continua_parametros_vencidos

    grupo_inclusoes = mommy.make(GrupoInclusaoAlimentacaoNormal, status=status)
    mommy.make(InclusaoAlimentacaoNormal, data=data_evento,
               grupo_inclusao=grupo_inclusoes)
    assert grupo_inclusoes in GrupoInclusaoAlimentacaoNormal.vencidos.all()
