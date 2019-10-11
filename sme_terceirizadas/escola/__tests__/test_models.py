import pytest

from ...dados_comuns.constants import DAQUI_A_30_DIAS, DAQUI_A_7_DIAS, SEM_FILTRO
from ..models import (
    DiretoriaRegional, TipoGestao, TipoUnidadeEscolar
)

pytestmark = pytest.mark.django_db


def test_tipo_unidade_escolar(tipo_unidade_escolar):
    assert isinstance(str(tipo_unidade_escolar), str)
    assert tipo_unidade_escolar.iniciais is not None
    assert tipo_unidade_escolar.cardapios.all() is not None


def test_tipo_gestao(tipo_gestao):
    assert isinstance(str(tipo_gestao), str)
    assert tipo_gestao.nome is not None


def test_diretoria_regional(diretoria_regional, escola):
    assert isinstance(str(diretoria_regional), str)
    assert diretoria_regional.nome is not None
    assert diretoria_regional.escolas is not None
    assert diretoria_regional.quantidade_alunos is not None
    assert escola in diretoria_regional.escolas.all()

    assert diretoria_regional.inclusoes_normais_autorizadas is not None
    assert diretoria_regional.inclusoes_continuas_reprovadas is not None
    assert diretoria_regional.inclusoes_normais_reprovadas is not None
    assert diretoria_regional.alteracoes_cardapio_pendentes_das_minhas_escolas is not None
    assert diretoria_regional.alteracoes_cardapio_autorizadas is not None
    assert diretoria_regional.solicitacao_kit_lanche_avulsa_aprovadas is not None
    assert diretoria_regional.solicitacao_kit_lanche_avulsa_reprovados is not None
    assert diretoria_regional.alteracoes_cardapio_reprovadas is not None
    assert diretoria_regional.inversoes_cardapio_autorizadas is not None
    assert diretoria_regional.inversoes_cardapio_reprovados is not None
    assert diretoria_regional.inclusoes_continuas_autorizadas is not None

    for filtro in [DAQUI_A_30_DIAS, DAQUI_A_7_DIAS, SEM_FILTRO]:
        assert diretoria_regional.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(filtro) is not None
        assert diretoria_regional.alteracoes_cardapio_das_minhas_escolas_a_validar(filtro) is not None
        assert diretoria_regional.inclusoes_alimentacao_continua_das_minhas_escolas(filtro) is not None
        assert diretoria_regional.alteracoes_cardapio_das_minhas_escolas(filtro) is not None
        assert diretoria_regional.inversoes_cardapio_das_minhas_escolas(filtro) is not None
        assert diretoria_regional.solicitacoes_pendentes(filtro) is not None

    assert diretoria_regional.solicitacoes_autorizadas() is not None


def test_escola(escola):
    assert isinstance(str(escola), str)
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

    assert escola.usuarios_diretoria_regional is not None
    assert escola.grupos_inclusoes is not None
    assert escola.inclusoes_continuas is not None


def test_faixa_idade_escolar(faixa_idade_escolar):
    assert isinstance(str(faixa_idade_escolar), str)
    assert faixa_idade_escolar.nome is not None


def test_codae(codae):
    assert isinstance(str(codae), str)
    assert codae.quantidade_alunos is not None
    assert codae.inversoes_cardapio_autorizadas is not None
    assert codae.inversoes_cardapio_reprovados is not None
    assert codae.solicitacoes_unificadas_aprovadas is not None
    assert codae.inclusoes_continuas_autorizadas is not None
    assert codae.inclusoes_normais_autorizadas is not None
    assert codae.inclusoes_continuas_reprovadas is not None
    assert codae.inclusoes_normais_reprovadas is not None
    assert codae.solicitacao_kit_lanche_avulsa_aprovadas is not None
    assert codae.solicitacao_kit_lanche_avulsa_reprovadas is not None
    assert codae.alteracoes_cardapio_autorizadas is not None
    assert codae.alteracoes_cardapio_reprovadas is not None

    for filtro in [DAQUI_A_30_DIAS, DAQUI_A_7_DIAS, SEM_FILTRO]:
        assert codae.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(filtro) is not None
        assert codae.solicitacoes_unificadas(filtro) is not None
        assert codae.suspensoes_cardapio_das_minhas_escolas(filtro) is not None
        assert codae.alteracoes_cardapio_das_minhas(filtro) is not None
        assert codae.inclusoes_alimentacao_continua_das_minhas_escolas(filtro) is not None
        assert codae.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(filtro) is not None
        assert codae.inversoes_cardapio_das_minhas_escolas(filtro) is not None


def test_lote(lote):
    assert isinstance(str(lote), str)
    assert lote.escolas is not None


def test_periodo_escolar(periodo_escolar):
    assert isinstance(str(periodo_escolar), str)


def test_sub_prefeitura(sub_prefeitura):
    assert isinstance(str(sub_prefeitura), str)
