from datetime import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from ...escola import models
from ..models.guia import ConferenciaIndividualPorAlimento

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def distribuidor():
    return mommy.make('Usuario', email='distribuidor@admin.com', is_superuser=True)


@pytest.fixture
def terceirizada():
    return mommy.make('Terceirizada',
                      contatos=[mommy.make('dados_comuns.Contato')],
                      make_m2m=True,
                      nome_fantasia='Alimentos SA'
                      )


@pytest.fixture
def solicitacao(terceirizada):
    return mommy.make(
        'SolicitacaoRemessa',
        cnpj='12345678901234',
        numero_solicitacao='559890',
        sequencia_envio=1212,
        quantidade_total_guias=2,
        distribuidor=terceirizada
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
def escola_com_guia(lote):
    return models.Escola.objects.get(uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')


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
def guia_pendente_de_conferencia(solicitacao, escola):
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
        telefone_unidade='944462050',
        status='PENDENTE_DE_CONFERENCIA'
    )


@pytest.fixture
def guia_com_escola_client_autenticado(solicitacao, escola_com_guia):
    return mommy.make(
        'Guia',
        solicitacao=solicitacao,
        escola=escola_com_guia,
        numero_guia='9876543',
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
        telefone_unidade='944462050',
        status='PENDENTE_DE_CONFERENCIA'
    )


@pytest.fixture
def alimento(guia_com_escola_client_autenticado):
    return mommy.make(
        'logistica.Alimento',
        guia=guia_com_escola_client_autenticado,
        codigo_suprimento='123456',
        codigo_papa='2345',
        nome_alimento='PATINHO'
    )


@pytest.fixture
def embalagem(alimento):
    return mommy.make(
        'Embalagem',
        alimento=alimento,
        descricao_embalagem='CX',
        capacidade_embalagem=9.13,
        unidade_medida='KG',
        tipo_embalagem='FECHADA',
        qtd_volume=90,
        qtd_a_receber=0
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


@pytest.fixture
def conferencia_guia(guia_com_escola_client_autenticado):
    return mommy.make(
        'ConferenciaGuia',
        guia=guia_com_escola_client_autenticado,
        data_recebimento=datetime.now(),
        hora_recebimento=datetime.now().time(),
        nome_motorista='José da Silva',
        placa_veiculo='77AB75A',
    )


@pytest.fixture
def conferencia_guia_normal(guia):
    return mommy.make(
        'ConferenciaGuia',
        guia=guia,
        data_recebimento=datetime.now(),
        hora_recebimento=datetime.now().time(),
        nome_motorista='José da Silva',
        placa_veiculo='77AB75A',
    )


@pytest.fixture
def reposicao_guia(guia):
    return mommy.make(
        'ConferenciaGuia',
        guia=guia,
        data_recebimento=datetime.now(),
        hora_recebimento=datetime.now().time(),
        nome_motorista='José da Silva',
        placa_veiculo='77AB75A',
        eh_reposicao=True
    )


@pytest.fixture
def conferencia_guia_individual(conferencia_guia_normal):
    return mommy.make(
        'ConferenciaIndividualPorAlimento',
        conferencia=conferencia_guia_normal,
        tipo_embalagem=ConferenciaIndividualPorAlimento.FECHADA,
        status_alimento=ConferenciaIndividualPorAlimento.STATUS_ALIMENTO_RECEBIDO,
        ocorrencia=[ConferenciaIndividualPorAlimento.OCORRENCIA_AUSENCIA_PRODUTO],
        nome_alimento='PATINHO',
        qtd_recebido=20,
    )


@pytest.fixture
def insucesso_entrega_guia(guia):
    return mommy.make(
        'InsucessoEntregaGuia',
        guia=guia,
        hora_tentativa=datetime.now().time(),
        nome_motorista='José da Silva',
        placa_veiculo='77AB75A',
        justificativa='Unidade estava fechada.',
        motivo='UNIDADE_FECHADA'
    )


@pytest.fixture
def solicitacao_cancelamento_log(solicitacao):
    return mommy.make(
        'LogSolicitacaoDeCancelamentoPeloPapa',
        requisicao=solicitacao,
        guias=['21236', '235264'],
        sequencia_envio='123456',
        foi_confirmada=False
    )
