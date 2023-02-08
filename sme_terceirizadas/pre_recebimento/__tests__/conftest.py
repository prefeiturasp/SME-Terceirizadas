
import pytest
from model_mommy import mommy

from sme_terceirizadas.terceirizada.models import Terceirizada


@pytest.fixture
def contrato():
    return mommy.make('Contrato',
                      numero='0003/2022',
                      processo='123')


@pytest.fixture
def empresa(contrato):
    return mommy.make(Terceirizada,
                      nome_fantasia='Alimentos SA',
                      contratos=[contrato],
                      tipo_servico=Terceirizada.FORNECEDOR,
                      )


@pytest.fixture
def cronograma():
    return mommy.make('Cronograma', numero='001/2022')


@pytest.fixture
def cronograma_rascunho(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        armazem=armazem,
        empresa=empresa,
    )


@pytest.fixture
def cronograma_recebido(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='ENVIADO_AO_FORNECEDOR'
    )


@pytest.fixture
def etapa(cronograma):
    return mommy.make('EtapasDoCronograma', cronograma=cronograma, etapa='Etapa 1')


@pytest.fixture
def programacao(cronograma):
    return mommy.make('ProgramacaoDoRecebimentoDoCronograma', cronograma=cronograma, data_programada='01/01/2022')


@pytest.fixture
def armazem():
    return mommy.make(Terceirizada,
                      nome_fantasia='Alimentos SA',
                      tipo_servico=Terceirizada.DISTRIBUIDOR_ARMAZEM,
                      )


@pytest.fixture
def laboratorio():
    return mommy.make('Laboratorio', nome='Labo Test')


@pytest.fixture
def emabalagem_qld():
    return mommy.make('EmbalagemQld', nome='CAIXA', abreviacao='CX')


@pytest.fixture
def cronograma_validado_fornecedor(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='VALIDADO_FORNECEDOR'
    )
