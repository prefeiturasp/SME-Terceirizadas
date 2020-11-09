import pytest
from model_mommy import mommy


@pytest.fixture
def solicitacao():
    return mommy.make(
        'SolicitacaoRemessa',
        cnpj='12345678901234',
        numero_solicitacao='559890'
    )


@pytest.fixture
def guia(solicitacao):
    return mommy.make(
        'Guia',
        solicitacao=solicitacao,
        numero_guia='987654',
        data_entrega='2019-02-25',
        codigo_unidade='58880',
        nome_unidade='EMEI ALUISIO DE ALMEIDA',
        endereco_unidade='Rua Alvaro de Azevedo Antunes',
        numero_unidade='1200',
        bairro_unidade='VILA CAMPESINA',
        cep_unidade='03046059',
        cidade_unidade='OSASCO',
        estado_unidade='SP',
        contato_unidade='Carlos',
        telefone_unidade='944462050'
    )
