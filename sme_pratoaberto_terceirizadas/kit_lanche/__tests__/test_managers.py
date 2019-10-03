import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy

from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...kit_lanche.models import SolicitacaoKitLancheAvulsa

pytestmark = pytest.mark.django_db


def monta_kit_lanche_avulso(kits_avulsos_datas, status=PedidoAPartirDaEscolaWorkflow.RASCUNHO):
    solicitacao_kit_lanche_base = mommy.make('SolicitacaoKitLanche', data=datetime.date(*kits_avulsos_datas))
    solicitacao_kit_lanche_avulsa = mommy.make('SolicitacaoKitLancheAvulsa',
                                               status=status,
                                               solicitacao_kit_lanche=solicitacao_kit_lanche_base)
    return solicitacao_kit_lanche_avulsa


@freeze_time('2019-10-03')
def test_manager_vencido(kits_avulsos_datas_passado_parametros):
    kits_avulsos_datas, status = kits_avulsos_datas_passado_parametros
    solicitacao_kit_lanche_avulsa = monta_kit_lanche_avulso(kits_avulsos_datas, status)
    assert solicitacao_kit_lanche_avulsa in SolicitacaoKitLancheAvulsa.vencidos.all()


@freeze_time('2019-10-03')
def test_manager_desta_semana(kits_avulsos_datas_semana):
    solicitacao_kit_lanche_avulsa = monta_kit_lanche_avulso(kits_avulsos_datas_semana)
    assert solicitacao_kit_lanche_avulsa in SolicitacaoKitLancheAvulsa.desta_semana.all()


@freeze_time('2019-10-03')
def test_manager_deste_mes(kits_avulsos_datas_mes):
    solicitacao_kit_lanche_avulsa = monta_kit_lanche_avulso(kits_avulsos_datas_mes)
    assert solicitacao_kit_lanche_avulsa in SolicitacaoKitLancheAvulsa.deste_mes.all()
