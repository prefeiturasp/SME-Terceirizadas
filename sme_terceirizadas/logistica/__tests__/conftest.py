import pytest
from faker import Faker
from model_mommy import mommy

from ...escola import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def distribuidor():
    return mommy.make('Usuario', email='distribuidor@admin.com', is_superuser=True)


@pytest.fixture
def solicitacao():
    return mommy.make(
        'SolicitacaoRemessa',
        cnpj='12345678901234',
        numero_solicitacao='559890',
        quantidade_total_guias=2
    )

@pytest.fixture
def lote():
    return mommy.make(models.Lote, nome='lote', iniciais='lt')

@pytest.fixture
def escola(lote):
    return mommy.make(models.Escola,
                      nome=fake.name(),
                      codigo_eol=fake.name()[:6],
                      lote=lote)

@pytest.fixture
def guia(solicitacao, escola):
    return mommy.make(
        'Guia',
        solicitacao=solicitacao,
        escola=escola,
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


@pytest.fixture
def solicitacao_de_alteracao_requisicao(solicitacao, distribuidor):
    return mommy.make(
        'SolicitacaoDeAlteracaoRequisicao',
        requisicao=solicitacao,
        motivo='OUTROS',
        justificativa=fake.text(),
        justificativa_aceite=fake.text(),
        justificativa_negacao=fake.text(),
        usuario_solicitante=distribuidor,
        numero_solicitacao='00000001-ALT',
    )
