from uuid import UUID

import pytest
from model_mommy import mommy
from xworkflows.base import InvalidTransitionError

from ..models import MotivoInclusaoContinua
from ...escola.models import Escola, PeriodoEscolar

pytestmark = pytest.mark.django_db


def test_motivo_inclusao_continua(motivo_inclusao_continua):
    assert isinstance(motivo_inclusao_continua.nome, str)
    assert isinstance(motivo_inclusao_continua.uuid, UUID)


def test_motivo_inclusao_normal(motivo_inclusao_normal):
    assert isinstance(motivo_inclusao_normal.nome, str)
    assert isinstance(motivo_inclusao_normal.uuid, UUID)


def test_quantidade_por_periodo(quantidade_por_periodo):
    assert isinstance(quantidade_por_periodo.numero_alunos, int)
    assert isinstance(quantidade_por_periodo.periodo_escolar, PeriodoEscolar)
    assert quantidade_por_periodo.tipos_alimentacao.all().count() == 5


def test_inclusao_alimentacao_continua(inclusao_alimentacao_continua):
    assert isinstance(inclusao_alimentacao_continua.escola, Escola)
    assert isinstance(inclusao_alimentacao_continua.motivo, MotivoInclusaoContinua)
    assunto, template_html = inclusao_alimentacao_continua.template_mensagem
    assert assunto == 'TESTE'
    assert '98DC7' in template_html
    assert 'RASCUNHO' in template_html


def test_inclusao_alimentacao_continua_fluxo(inclusao_alimentacao_continua):
    fake_user = mommy.make('perfil.Usuario')
    inclusao_alimentacao_continua.inicia_fluxo(user=fake_user)
    assert inclusao_alimentacao_continua.ta_na_dre
    inclusao_alimentacao_continua.dre_aprovou(user=fake_user)
    assert inclusao_alimentacao_continua.ta_na_codae
    inclusao_alimentacao_continua.codae_aprovou(user=fake_user)
    assert inclusao_alimentacao_continua.ta_na_terceirizada


def test_inclusao_alimentacao_continua_fluxo_erro(inclusao_alimentacao_continua):
    # TODO: pedir incremento do fluxo para testá-lo por completo
    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_pediu_revisao' isn't available from state 'RASCUNHO'."):
        inclusao_alimentacao_continua.dre_pediu_revisao()
