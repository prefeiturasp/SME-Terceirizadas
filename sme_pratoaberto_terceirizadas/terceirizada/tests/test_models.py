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



