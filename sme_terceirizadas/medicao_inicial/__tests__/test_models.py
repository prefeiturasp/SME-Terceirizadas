import pytest

pytestmark = pytest.mark.django_db


def test_dia_sobremesa_doce_model(dia_sobremesa_doce):
    assert dia_sobremesa_doce.__str__() == '08/08/2022 - EMEF'


def test_solicitacao_medicao_inicial_model(solicitacao_medicao_inicial):
    assert solicitacao_medicao_inicial.__str__() == 'Solicitação #BED4D -- Escola EMEF TESTE -- 12/2022'


def test_anexo_ocorrencia_medicao_inicial_model(anexo_ocorrencia_medicao_inicial):
    str_model = 'Anexo Ocorrência 1ace193a-6c2c-4686-b9ed-60a922ad0e1a - arquivo_teste.pdf'
    assert anexo_ocorrencia_medicao_inicial.__str__() == str_model


def test_responsavel_model(responsavel):
    assert responsavel.__str__() == 'Responsável tester - 1234567'


def test_tipo_contagem_alimentacao_model(tipo_contagem_alimentacao):
    assert tipo_contagem_alimentacao.__str__() == 'Fichas'


def test_medicao_model(medicao):
    assert medicao.__str__() == 'Medição #5A3A3 -- INTEGRAL -- 12/2022'


def test_categoria_medicao_model(categoria_medicao):
    assert categoria_medicao.__str__() == 'ALIMENTAÇÃO'


def test_valor_medicao_model(valor_medicao):
    assert valor_medicao.__str__() == '#FC2FB -- Categoria ALIMENTAÇÃO -- Campo observacoes -- Dia/Mês 13/12'
