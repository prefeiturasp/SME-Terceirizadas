import pytest

from ..models import (
    DiretoriaRegional, TipoGestao, TipoUnidadeEscolar
)

pytestmark = pytest.mark.django_db


def test_tipo_unidade_escolar(tipo_unidade_escolar):
    assert tipo_unidade_escolar.iniciais is not None
    assert tipo_unidade_escolar.cardapios.all() is not None


def test_tipo_gestao(tipo_gestao):
    assert tipo_gestao.nome is not None


def test_diretoria_regional(diretoria_regional, escola):
    assert diretoria_regional.nome is not None
    assert diretoria_regional.escolas is not None
    assert diretoria_regional.quantidade_alunos is not None
    assert escola in diretoria_regional.escolas.all()

    assert diretoria_regional.inclusoes_normais_aprovadas is not None
    assert diretoria_regional.inclusoes_continuas_reprovadas is not None
    assert diretoria_regional.inclusoes_normais_reprovadas is not None
    assert diretoria_regional.alteracoes_cardapio_pendentes_das_minhas_escolas is not None
    assert diretoria_regional.alteracoes_cardapio_aprovadas is not None
    assert diretoria_regional.solicitacao_kit_lanche_avulsa_aprovadas is not None
    assert diretoria_regional.solicitacao_kit_lanche_avulsa_reprovados is not None
    assert diretoria_regional.alteracoes_cardapio_reprovadas is not None
    assert diretoria_regional.inversoes_cardapio_aprovadas is not None
    assert diretoria_regional.inversoes_cardapio_reprovados is not None


def test_escola(escola):
    assert escola.nome is not None
    assert escola.codigo_eol is not None
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


def test_codae(codae):
    assert codae.quantidade_alunos is not None
    assert codae.inversoes_cardapio_aprovadas is not None
    assert codae.inversoes_cardapio_reprovados is not None
    assert codae.solicitacoes_unificadas_aprovadas is not None
    assert codae.inclusoes_continuas_aprovadas is not None
    assert codae.inclusoes_normais_aprovadas is not None
    assert codae.inclusoes_continuas_reprovadas is not None
    assert codae.inclusoes_normais_reprovadas is not None
    assert codae.solicitacao_kit_lanche_avulsa_aprovadas is not None
    assert codae.solicitacao_kit_lanche_avulsa_reprovadas is not None
    assert codae.alteracoes_cardapio_aprovadas is not None
    assert codae.alteracoes_cardapio_reprovadas is not None
