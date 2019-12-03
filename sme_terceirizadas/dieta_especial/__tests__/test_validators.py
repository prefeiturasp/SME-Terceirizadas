import pytest
from rest_framework.exceptions import ValidationError

from ..api.validators import deve_ter_extensao_valida

pytestmark = pytest.mark.django_db


def test_extensoes_validas(nomes_arquivos_validos):
    nome = deve_ter_extensao_valida(nomes_arquivos_validos)
    assert type(nome) is str


def test_extensoes_invalidas(nomes_arquivos_invalidos):
    with pytest.raises(ValidationError, match='Extensão inválida'):
        deve_ter_extensao_valida(nomes_arquivos_invalidos)
