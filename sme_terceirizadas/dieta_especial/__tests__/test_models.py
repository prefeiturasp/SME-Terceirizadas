import pytest

pytestmark = pytest.mark.django_db


def test_solicitacao_dieta_especial_obj(solicitacao_dieta_especial):
    assert solicitacao_dieta_especial.__str__() == '123456: Roberto Alves da Silva'
    assert solicitacao_dieta_especial.escola == solicitacao_dieta_especial.rastro_escola


def test_anexo_obj(anexo_docx):
    assert anexo_docx.nome == anexo_docx.arquivo.url
