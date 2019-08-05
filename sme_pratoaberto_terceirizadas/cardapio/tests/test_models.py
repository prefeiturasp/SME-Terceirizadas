import pytest
from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.cardapio.models import Cardapio

pytestmark = pytest.mark.django_db


def test_motivo_alteracao_cardapio(motivo_alteracao_cardapio):
    assert motivo_alteracao_cardapio.nome is not None


def test_alteracao_cardapio(alteracao_cardapio):
    assert alteracao_cardapio.data_inicial is not None
    assert alteracao_cardapio.data_final is not None
    assert alteracao_cardapio.observacao == "teste"
    assert alteracao_cardapio.status is not None


def test_substituicoes_alimentacao_periodo(substituicoes_alimentacao_periodo):
    assert substituicoes_alimentacao_periodo.qtd_alunos is not None
    assert substituicoes_alimentacao_periodo.alteracao_cardapio is not None
    assert substituicoes_alimentacao_periodo.alteracao_cardapio.substituicoes is not None


def test_inversao_dia_cardapio(inversao_dia_cardapio):
    assert isinstance(inversao_dia_cardapio.escola, Escola)
    assert isinstance(inversao_dia_cardapio.cardapio_de, Cardapio)
    assert isinstance(inversao_dia_cardapio.cardapio_para, Cardapio)
    assunto, template_html = inversao_dia_cardapio.template_mensagem
    assert assunto == 'TESTE INVERSAO CARDAPIO'
    assert '98DC7' in template_html
    assert 'RASCUNHO' in template_html
