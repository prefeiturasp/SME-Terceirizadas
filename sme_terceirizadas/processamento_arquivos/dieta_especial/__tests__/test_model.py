import pytest

from sme_terceirizadas.dados_comuns.constants import StatusProcessamentoArquivo
from sme_terceirizadas.dieta_especial.models import (
    ArquivoCargaAlimentosSubstitutos,
    ArquivoCargaDietaEspecial,
    ArquivoCargaUsuariosEscola
)

pytestmark = pytest.mark.django_db


def test_model_arquivo_carga_dieta_especial(arquivo_carga_dieta_especial):
    model = arquivo_carga_dieta_especial
    assert isinstance(model, ArquivoCargaDietaEspecial)
    assert model.status == StatusProcessamentoArquivo.PENDENTE.value


def test_model_arquivo_carga_usuarios_escola(arquivo_carga_usuarios_escola):
    model = arquivo_carga_usuarios_escola
    assert isinstance(model, ArquivoCargaUsuariosEscola)
    assert model.status == StatusProcessamentoArquivo.PENDENTE.value


def test_model_arquivo_carga_alimentos_e_substitutos(arquivo_carga_alimentos_e_substitutos):
    model = arquivo_carga_alimentos_e_substitutos
    assert isinstance(model, ArquivoCargaAlimentosSubstitutos)
    assert model.status == StatusProcessamentoArquivo.PENDENTE.value
