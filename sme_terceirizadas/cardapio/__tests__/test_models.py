import pytest
from model_mommy import mommy
from xworkflows.base import InvalidTransitionError

from ...cardapio.models import Cardapio
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...escola.models import Escola

pytestmark = pytest.mark.django_db


def test_tipo_alimentacao(tipo_alimentacao):
    assert tipo_alimentacao.__str__() == 'Refeição'


def test_motivo_alteracao_cardapio(motivo_alteracao_cardapio):
    assert motivo_alteracao_cardapio.nome is not None
    assert motivo_alteracao_cardapio.__str__() == 'Aniversariantes do mês'


def test_motivo_suspensao_alimentacao(motivo_suspensao_alimentacao):
    assert motivo_suspensao_alimentacao.__str__() == 'Não vai ter aula'


def test_quantidade_por_periodo_suspensao_alimentacao(quantidade_por_periodo_suspensao_alimentacao):
    assert quantidade_por_periodo_suspensao_alimentacao.__str__() == 'Quantidade de alunos: 100'


def test_suspensao_alimentacao(suspensao_alimentacao):
    assert suspensao_alimentacao.__str__() == 'Não vai ter aula'


def test_suspensao_alimentacao_no_periodo_escolar(suspensao_periodo_escolar):
    assert suspensao_periodo_escolar.__str__() == 'Suspensão de alimentação da Alteração de Cardápio: Não vai ter aula'


def test_alteracao_cardapio(alteracao_cardapio):
    assert alteracao_cardapio.data_inicial is not None
    assert alteracao_cardapio.data_final is not None
    assert alteracao_cardapio.observacao == 'teste'
    assert alteracao_cardapio.status is not None
    assert alteracao_cardapio.__str__() == 'Alteração de cardápio de: 2019-10-04 para 2019-12-31'


def test_substituicoes_alimentacao_periodo(substituicoes_alimentacao_periodo):
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


def test_inversao_dia_cardapio_fluxo(inversao_dia_cardapio):
    fake_user = mommy.make('perfil.Usuario')
    inversao_dia_cardapio.inicia_fluxo(user=fake_user)
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    inversao_dia_cardapio.dre_valida(user=fake_user)
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO


def test_inversao_dia_cardapio_fluxo_cancelamento(inversao_dia_cardapio):
    fake_user = mommy.make('perfil.Usuario')
    inversao_dia_cardapio.inicia_fluxo(user=fake_user)
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    inversao_dia_cardapio.cancelar_pedido(user=fake_user)
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU


def test_inversao_dia_cardapio_fluxo_cancelamento_erro(inversao_dia_cardapio2):
    fake_user = mommy.make('perfil.Usuario')
    with pytest.raises(
        InvalidTransitionError,
        match=r'.*Só pode cancelar com no mínimo 2 dia\(s\) de antecedência.*'
    ):
        inversao_dia_cardapio2.inicia_fluxo(user=fake_user)
        inversao_dia_cardapio2.cancelar_pedido(user=fake_user)


def test_inclusao_alimentacao_continua_fluxo_erro(inversao_dia_cardapio):
    # TODO: pedir incremento do fluxo para testá-lo por completo
    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_pede_revisao' isn't available from state 'RASCUNHO'."):
        inversao_dia_cardapio.dre_pede_revisao()


def test_grupo_suspensao_alimentacao(grupo_suspensao_alimentacao):
    assert grupo_suspensao_alimentacao.__str__() == 'lorem ipsum'
