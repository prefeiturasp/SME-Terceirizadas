import pytest

from ..models import (
    DiretoriaRegional, TipoUnidadeEscolar, TipoGestao, Lote
)

pytestmark = pytest.mark.django_db


def test_tipo_unidade_escolar(tipo_unidade_escolar):
    assert tipo_unidade_escolar.iniciais is not None
    assert tipo_unidade_escolar.cardapios.all() is not None


def test_tipo_gestao(tipo_gestao):
    assert tipo_gestao.nome is not None


def test_diretoria_regional(diretoria_regional):
    assert diretoria_regional.nome is not None
    assert diretoria_regional.escolas is not None


def test_escola(escola):
    assert escola.nome is not None
    assert escola.codigo_eol is not None
    assert escola.codigo_codae is not None
    assert escola.quantidade_alunos is not None
    assert isinstance(escola.diretoria_regional, DiretoriaRegional)
    assert isinstance(escola.tipo_unidade, TipoUnidadeEscolar)
    assert isinstance(escola.tipo_gestao, TipoGestao)
    assert escola.lote is None
    assert escola.idades.all() is not None
    assert escola.periodos_escolares.all() is not None
    assert escola.usuarios.all() is not None


def test_faixa_idade_escolar(faixa_idade_escolar):
    assert faixa_idade_escolar.nome is not None
