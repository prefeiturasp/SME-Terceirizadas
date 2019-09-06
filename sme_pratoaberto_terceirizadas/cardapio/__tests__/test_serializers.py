import pytest

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
    assert 'qtd_alunos' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
    assert 'periodo_escolar' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
    assert 'tipos_alimentacao' in substituicoes_alimentacao_no_periodo_escolar_serializer.data
