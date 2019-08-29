import pytest
from model_mommy import mommy

from ...dados_comuns.models_abstract import TempoPasseio

pytestmark = pytest.mark.django_db


def test_kit_lanche(kit_lanche):
    assert isinstance(kit_lanche.nome, str)
    assert isinstance(kit_lanche.__str__(), str)
    assert kit_lanche.itens.count() == 3
    assert kit_lanche._meta.verbose_name == 'Kit lanche'
    assert kit_lanche._meta.verbose_name_plural == 'Kit lanches'


def test_item_kit_lanche(item_kit_lanche):
    assert isinstance(item_kit_lanche.nome, str)
    assert isinstance(item_kit_lanche.__str__(), str)


def test_solicitacao_avulsa(solicitacao_avulsa):
    assert isinstance(solicitacao_avulsa.local, str)
    assert solicitacao_avulsa.quantidade_alunos == 999
    assert 'Solicitação' in solicitacao_avulsa._meta.verbose_name


def test_solicitacao_unificada(solicitacao_unificada_lista_igual):
    assert isinstance(solicitacao_unificada_lista_igual.local, str)
    assert solicitacao_unificada_lista_igual.lista_kit_lanche_igual is True

    escolas_quantidades = mommy.make('EscolaQuantidade', _quantity=10, quantidade_alunos=100)
    assert solicitacao_unificada_lista_igual.vincula_escolas_quantidades(
        escolas_quantidades) is None
    assert solicitacao_unificada_lista_igual.total_kit_lanche == 3000


def test_solicitacao(solicitacao):
    assert solicitacao.tempo_passeio == TempoPasseio.CINCO_A_SETE
    assert solicitacao.kits.count() == 3
    assert 'Solicitação kit lanche base' in solicitacao._meta.verbose_name
