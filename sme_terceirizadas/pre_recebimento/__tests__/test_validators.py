import pytest
from rest_framework.serializers import ValidationError

from ..api.validators import contrato_pertence_a_empresa

pytestmark = pytest.mark.django_db


def test_contrato_pertence_a_empresa_validator(contrato, empresa):
    """Deve retornar True caso o contrato pertença à empresa ou lançar um ValidationError caso contrário."""
    assert contrato_pertence_a_empresa(contrato, empresa)

    empresa.contratos.clear()

    with pytest.raises(ValidationError, match='Contrato deve pertencer a empresa selecionada'):
        contrato_pertence_a_empresa(contrato, empresa)
