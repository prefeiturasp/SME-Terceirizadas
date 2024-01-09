import pytest

from sme_terceirizadas.medicao_inicial.validators import (
    valida_medicoes_inexistentes_cei,
    validate_lancamento_alimentacoes_medicao_cei,
    validate_lancamento_inclusoes_cei,
    validate_lancamento_inclusoes_dietas_emef,
    validate_solicitacoes_etec,
    validate_solicitacoes_programas_e_projetos,
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


def test_validate_lancamento_inclusoes_dietas_emef(
    solicitacao_medicao_inicial_teste_salvar_logs,
):
    lista_erros = []
    lista_erros = validate_lancamento_inclusoes_dietas_emef(
        solicitacao_medicao_inicial_teste_salvar_logs, lista_erros
    )
    assert len(lista_erros) == 0


def test_validate_solicitacoes_etec(
    solicitacao_medicao_inicial_teste_salvar_logs,
):
    lista_erros = []
    lista_erros = validate_solicitacoes_etec(
        solicitacao_medicao_inicial_teste_salvar_logs, lista_erros
    )
    assert len(lista_erros) == 0


def test_validate_solicitacoes_programas_e_projetos(
    solicitacao_medicao_inicial_teste_salvar_logs,
):
    lista_erros = []
    lista_erros = validate_solicitacoes_programas_e_projetos(
        solicitacao_medicao_inicial_teste_salvar_logs, lista_erros
    )
    assert len(lista_erros) == 0
