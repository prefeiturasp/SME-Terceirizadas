import pytest

from sme_terceirizadas.cardapio.api.serializers.serializers import VinculoTipoAlimentoSimplesSerializer, \
    SubstituicoesVinculoTipoAlimentoSimplesSerializer

pytestmark = pytest.mark.django_db


def test_inversao_cardapio_serializer(inversao_cardapio_serializer):
    assert inversao_cardapio_serializer.data is not None


def test_suspensao_alimentacao_serializer(suspensao_alimentacao_serializer):
    assert suspensao_alimentacao_serializer.data is not None


def test_motivo_alteracao_cardapio_serializer(motivo_alteracao_cardapio_serializer):
    assert motivo_alteracao_cardapio_serializer.data is not None
    assert 'nome' in motivo_alteracao_cardapio_serializer.data
    assert 'uuid' in motivo_alteracao_cardapio_serializer.data


def test_alteracao_cardapio_serializer(alteracao_cardapio_serializer):
    assert alteracao_cardapio_serializer.data is not None
    assert 'data_inicial' in alteracao_cardapio_serializer.data
    assert 'data_final' in alteracao_cardapio_serializer.data
    assert 'escola' in alteracao_cardapio_serializer.data
    assert 'substituicoes' in alteracao_cardapio_serializer.data


def test_substituicoes_alimentacao_no_periodo_escolar_serializer(  # noqa
    substituicoes_alimentacao_no_periodo_escolar_serializer):
    assert substituicoes_alimentacao_no_periodo_escolar_serializer is not None
    assert 'alteracao_cardapio' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
    assert 'periodo_escolar' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
    assert 'tipo_alimentacao_de' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
    assert 'tipo_alimentacao_para' in substituicoes_alimentacao_no_periodo_escolar_serializer.data


def test_vinculo_tipo_alimentacao_serializer(vinculo_tipo_alimentacao):
    vinculo_serializer = VinculoTipoAlimentoSimplesSerializer(vinculo_tipo_alimentacao)
    assert 'periodo_escolar' in vinculo_serializer.data
    assert 'tipo_unidade_escolar' in vinculo_serializer.data
    assert 'substituicoes' in vinculo_serializer.data


def test_substituicies_vinculo_tipo_alimentacao_serializer(substituicies_vinculo_tipo_alimentacao):
    substituicoes_vinculo_serializer = SubstituicoesVinculoTipoAlimentoSimplesSerializer(
        substituicies_vinculo_tipo_alimentacao,
        many=True)
    for substituicao in substituicoes_vinculo_serializer.data:
        assert 'tipo_alimentacao' in substituicao
        assert 'possibilidades' in substituicao
        assert 'substituicoes' in substituicao
