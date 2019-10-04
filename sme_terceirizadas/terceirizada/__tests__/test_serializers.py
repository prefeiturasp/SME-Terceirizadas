import pytest

pytestmark = pytest.mark.django_db


def test_vigencia_contrato_serializer(vigencia_contrato_serializer):
    assert vigencia_contrato_serializer.data is not None
    assert 'uuid' in vigencia_contrato_serializer.data
    assert 'data_inicial' in vigencia_contrato_serializer.data
    assert 'data_final' in vigencia_contrato_serializer.data


def test_contrato_serializer(contrato_serializer):
    assert contrato_serializer.data is not None
    assert 'uuid' in contrato_serializer.data
    assert 'numero' in contrato_serializer.data
    assert 'processo' in contrato_serializer.data
    assert 'data_proposta' in contrato_serializer.data
    assert 'lotes' in contrato_serializer.data
    assert 'terceirizada' in contrato_serializer.data
    assert 'edital' in contrato_serializer.data
    assert 'vigencias' in contrato_serializer.data


def test_edital_contratos_serializer(edital_contratos_serializer):
    assert edital_contratos_serializer.data is not None
    assert 'uuid' in edital_contratos_serializer.data
    assert 'numero' in edital_contratos_serializer.data
    assert 'tipo_contratacao' in edital_contratos_serializer.data
    assert 'processo' in edital_contratos_serializer.data
    assert 'objeto' in edital_contratos_serializer.data
    assert 'contratos' in edital_contratos_serializer.data
