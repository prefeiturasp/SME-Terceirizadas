
import pytest
from model_mommy import mommy


@pytest.fixture
def cronograma():
    return mommy.make('Cronograma', numero='001/2022')


@pytest.fixture
def etapas(cronograma):
    return mommy.make('EtapasDoCronograma', cronograma=cronograma, etapa='Etapa 1')


@pytest.fixture
def programacao(cronograma):
    return mommy.make('ProgramacaoDoRecebimentoDoCronograma', cronograma=cronograma, data_programada='01/01/2022')
