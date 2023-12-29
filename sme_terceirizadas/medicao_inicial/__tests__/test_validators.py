import pytest

from sme_terceirizadas.medicao_inicial.validators import (
    valida_medicoes_inexistentes_cei,
    validate_lancamento_alimentacoes_medicao_cei,
    validate_lancamento_inclusoes_cei,
)

pytestmark = pytest.mark.django_db


def test_valida_medicoes_inexistentes_cei(solicitacao_medicao_inicial_cei):
    lista_erros = []
    lista_erros = valida_medicoes_inexistentes_cei(
        solicitacao_medicao_inicial_cei, lista_erros
    )
    assert len(lista_erros) == 2
    assert (
        next((erro for erro in lista_erros if erro["periodo_escolar"] == "MANHA"), None)
        is not None
    )
    assert (
        next(
            (erro for erro in lista_erros if erro["periodo_escolar"] == "PARCIAL"), None
        )
        is not None
    )


def test_validate_lancamento_alimentacoes_medicao_cei(solicitacao_medicao_inicial_cei):
    lista_erros = []
    lista_erros = validate_lancamento_alimentacoes_medicao_cei(
        solicitacao_medicao_inicial_cei, lista_erros
    )
    assert len(lista_erros) == 0


def test_validate_lancamento_inclusoes_cei(solicitacao_medicao_inicial_cei):
    lista_erros = []
    lista_erros = validate_lancamento_inclusoes_cei(
        solicitacao_medicao_inicial_cei, lista_erros
    )
    assert len(lista_erros) == 0
