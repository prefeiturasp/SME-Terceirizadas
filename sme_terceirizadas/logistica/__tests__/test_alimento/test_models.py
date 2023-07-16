import pytest
from django.core.exceptions import ValidationError

from ...models import UnidadeMedida

pytestmark = pytest.mark.django_db


def test_unidade_medida_model(unidade_medida_logistica):
    """Deve possuir os campos nome e abreviacao"""

    assert unidade_medida_logistica.nome == 'UNIDADE TESTE'
    assert unidade_medida_logistica.abreviacao == 'ut'
