import pytest
from statemachine.exceptions import TransitionNotAllowed

from ..fluxo_status import ControleDeFluxoDeStatusAPartirDaEscola

pytestmark = pytest.mark.django_db


def test_fluxo_status_comecando_da_escola_fluxo1():
    controle = ControleDeFluxoDeStatusAPartirDaEscola()

    controle.comeca_fluxo()

    controle.dre_pediu_revisao()  # começa vai volta
    controle.escola_revisou()
    controle.dre_pediu_revisao()
    controle.escola_revisou()
    controle.dre_pediu_revisao()
    controle.escola_revisou()

    controle.dre_aprovou()
    controle.codae_aprovou()
    controle.terceirizada_toma_ciencia()  # fim


def test_fluxo_status_comecando_da_escola_fluxo2():
    controle = ControleDeFluxoDeStatusAPartirDaEscola()

    controle.comeca_fluxo()

    controle.dre_pediu_revisao()  # começa vai volta
    controle.escola_revisou()
    controle.dre_pediu_revisao()
    controle.escola_revisou()
    controle.dre_pediu_revisao()
    controle.escola_revisou()

    controle.dre_aprovou()
    controle.codae_recusou()  # fim


def test_fluxo_status_comecando_da_escola_erro():
    with pytest.raises(TransitionNotAllowed, match="Can't codae_aprovou when in DRE_A_VALIDAR."):
        controle = ControleDeFluxoDeStatusAPartirDaEscola()
        controle.comeca_fluxo()
        controle.dre_pediu_revisao()
        controle.escola_revisou()  # espera dre aprovar
        controle.codae_aprovou()
