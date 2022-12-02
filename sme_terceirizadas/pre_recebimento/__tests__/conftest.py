
import pytest
from model_mommy import mommy


@pytest.fixture
def cronograma():
    return mommy.make('Cronograma', numero='001/2022')


@pytest.fixture
def cronograma_rascunho(armazem):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato='1234/2022',
        contrato_uuid='f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
        armazem=armazem,
    )


@pytest.fixture
def etapa(cronograma):
    return mommy.make('EtapasDoCronograma', cronograma=cronograma, etapa='Etapa 1')


@pytest.fixture
def programacao(cronograma):
    return mommy.make('ProgramacaoDoRecebimentoDoCronograma', cronograma=cronograma, data_programada='01/01/2022')


@pytest.fixture
def armazem():
    return mommy.make('Terceirizada',
                      uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
                      nome_fantasia='Alimentos SA'
                      )


@pytest.fixture
def laboratorio():
    return mommy.make('Laboratorio', nome='Labo Test')


@pytest.fixture
def emabalagem_qld():
    return mommy.make('EmbalagemQld', nome='CAIXA', abreviacao='CX')
