import pytest
from django.conf import settings

from sme_terceirizadas.pre_recebimento.api.serializers.serializer_create import UnidadeMedidaCreateSerializer
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import UnidadeMedidaSerialzer
from sme_terceirizadas.pre_recebimento.models import UnidadeMedida

pytestmark = pytest.mark.django_db


def test_unidade_medida_serializer(unidade_medida_logistica):
    """Deve serializar corretamente a instância de Unidade de Medida."""
    serializer = UnidadeMedidaSerialzer(unidade_medida_logistica)

    drf_date_format = settings.REST_FRAMEWORK['DATETIME_FORMAT']

    assert serializer.data['uuid'] == str(unidade_medida_logistica.uuid)
    assert serializer.data['nome'] == str(unidade_medida_logistica.nome)
    assert serializer.data['abreviacao'] == str(unidade_medida_logistica.abreviacao)
    assert serializer.data['criado_em'] == unidade_medida_logistica.criado_em.strftime(drf_date_format)


def test_unidade_medida_create_serializer_creation():
    """Deve criar corretamente uma instância de Unidade de Medida."""
    data = {
        'nome': 'UNIDADE MEDIDA',
        'abreviacao': 'um'
    }

    serializer = UnidadeMedidaCreateSerializer(data=data)
    qtd_unidades_medida_antes = UnidadeMedida.objects.count()

    assert serializer.is_valid() is True
    assert serializer.validated_data['nome'] == data['nome']
    assert serializer.validated_data['abreviacao'] == data['abreviacao']

    instance = serializer.save()

    assert UnidadeMedida.objects.count() == qtd_unidades_medida_antes + 1
    assert instance.uuid is not None
    assert instance.criado_em is not None


def test_unidade_medida_create_serializer_updating(unidade_medida_logistica):
    """Deve criar corretamente uma instância de Unidade de Medida."""
    data = {
        'nome': 'UNIDADE MEDIDA ATUALIZADA',
        'abreviacao': 'uma'
    }

    serializer = UnidadeMedidaCreateSerializer(data=data, instance=unidade_medida_logistica)

    assert serializer.is_valid() is True
    assert serializer.validated_data['nome'] == data['nome']
    assert serializer.validated_data['abreviacao'] == data['abreviacao']
