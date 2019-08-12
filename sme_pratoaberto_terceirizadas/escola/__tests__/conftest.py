import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def tipo_unidade_escolar():
    return mommy.make(models.TipoUnidadeEscolar,
                      iniciais=fake.name()[:10])


@pytest.fixture
def tipo_gestao():
    return mommy.make(models.TipoGestao,
                      nome=fake.name())


@pytest.fixture
def diretoria_regional():
    return mommy.make(models.DiretoriaRegional,
                      nome=fake.name())


@pytest.fixture
def escola():
    return mommy.make(models.Escola,
                      nome=fake.name(),
                      codigo_eol=fake.name()[:6],
                      codigo_codae=fake.name()[:6],
                      quantidade_alunos=42)


@pytest.fixture
def faixa_idade_escolar():
    return mommy.make(models.FaixaIdadeEscolar,
                      nome=fake.name())
