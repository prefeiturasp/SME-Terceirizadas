import pytest
from model_mommy import mommy

from sme_terceirizadas.dieta_especial.models import (
    ArquivoCargaAlimentosSubstitutos,
    ArquivoCargaDietaEspecial,
    ArquivoCargaUsuariosEscola
)


@pytest.fixture
def arquivo_carga_dieta_especial():
    return mommy.make(ArquivoCargaDietaEspecial)


@pytest.fixture
def arquivo_carga_alimentos_e_substitutos():
    return mommy.make(ArquivoCargaAlimentosSubstitutos)


@pytest.fixture
def arquivo_carga_usuarios_escola():
    return mommy.make(ArquivoCargaUsuariosEscola)
