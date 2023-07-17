import pytest
from django.conf import settings

from ...api.serializers.serializers import UnidadeMedidaSerialzer

pytestmark = pytest.mark.django_db


def test_unidade_medida_serializer_serialization(unidade_medida_logistica):
    """Deve serializar corretamente a instância de Unidade de Medida."""
    serializer = UnidadeMedidaSerialzer(unidade_medida_logistica)

    drf_date_format = settings.REST_FRAMEWORK['DATETIME_FORMAT']

    assert serializer.data['uuid'] == str(unidade_medida_logistica.uuid)
    assert serializer.data['nome'] == str(unidade_medida_logistica.nome)
    assert serializer.data['abreviacao'] == str(unidade_medida_logistica.abreviacao)
    assert serializer.data['criado_em'] == unidade_medida_logistica.criado_em.strftime(drf_date_format)


def test_unidade_medida_serializer_deserialization():
    """Deve criar corretamente uma instância de Unidade de Medida."""
    data = {
        'nome': 'UNIDADE MEDIDA',
        'abreviacao': 'um'
    }

    serializer = UnidadeMedidaSerialzer(data=data)

    assert serializer.is_valid() is True
    assert serializer.validated_data['nome'] == data['nome']
    assert serializer.validated_data['abreviacao'] == data['abreviacao']

    serializer.save()
    assert serializer.data['uuid'] is not None
    assert serializer.data['criado_em'] is not None


def test_unidade_medida_serializer_nome_validation():
    """Deve ser inválido para desserialização de objeto cujo atributo nome não esteja em caixa alta."""
    data = {
        'nome': 'unidade de medida',
        'abreviacao': 'um'
    }

    expected_error_title = 'O campo deve conter apenas letras maiúsculas.'

    serializer = UnidadeMedidaSerialzer(data=data)

    assert serializer.is_valid() is False
    assert str(serializer.errors['nome'][0]) == expected_error_title


def test_unidade_medida_serializer_abreviacao_validation():
    """Deve ser inválido para desserialização de objeto cujo atributo abreviacao não esteja em caixa baixa."""
    data = {
        'nome': 'UNIDADE DE MEDIDA',
        'abreviacao': 'UM'
    }

    expected_error_title = 'O campo deve conter apenas letras minúsculas.'

    serializer = UnidadeMedidaSerialzer(data=data)

    assert serializer.is_valid() is False
    assert str(serializer.errors['abreviacao'][0]) == expected_error_title
