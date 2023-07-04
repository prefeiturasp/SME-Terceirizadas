import pytest

pytestmark = pytest.mark.django_db


def test_vinculo_instituto_serializer(vinculo_instituto_serializer):
    assert vinculo_instituto_serializer.data is not None


def test_escola_simplissima_serializer(escola_simplissima_serializer):
    assert escola_simplissima_serializer.data is not None


def test_escola_simplissima_contem_campos_esperados(escola_simplissima_serializer):  # noqa
    esperado = set(['uuid', 'nome', 'codigo_eol', 'codigo_codae', 'diretoria_regional',
                    'lote', 'quantidade_alunos', 'tipo_gestao'])
    resultado = escola_simplissima_serializer.data.keys()
    assert esperado == resultado
