from model_mommy import mommy
import pytest
from xworkflows.base import InvalidTransitionError

from sme_pratoaberto_terceirizadas.terceirizada.models import Edital


pytestmark = pytest.mark.django_db


def test_modelo_edital(edital):
    assert edital.uuid is not None
    assert edital.tipo_contratacao is not None
    assert edital.numero is not None
    assert edital.processo is not None
    assert edital.numero is not None
    assert edital.objeto is not None
    assert edital.contratos is not None


def test_modelo_contrato(contrato):
    assert contrato.uuid is not None
    assert contrato.numero is not None
    assert contrato.processo is not None
    assert contrato.data_proposta is not None
    assert contrato.lotes is not None
    assert contrato.terceirizadas is not None
    assert contrato.vigencias is not None
    # assert contrato.edital is not None


def test_modelo_vigencia_contrato(vigencia_contrato):
    assert vigencia_contrato.uuid is not None
    assert vigencia_contrato.data_inicial is not None
    assert vigencia_contrato.data_final is not None
