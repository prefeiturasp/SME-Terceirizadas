import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def tipo_unidade_escolar():
    cardapio1 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 15))
    return mommy.make(models.TipoUnidadeEscolar,
                      iniciais=fake.name()[:10],
                      cardapios=[cardapio1, cardapio2])


@pytest.fixture
def tipo_gestao():
    return mommy.make(models.TipoGestao,
                      nome=fake.name())


@pytest.fixture
def diretoria_regional(escola):
    return mommy.make(models.DiretoriaRegional,
                      escolas=[escola],
                      nome=fake.name(),
                      make_m2m=True)


@pytest.fixture
def escola():
    return mommy.make(models.Escola,
                      nome=fake.name(),
                      codigo_eol=fake.name()[:6],
                      quantidade_alunos=42)


@pytest.fixture
def faixa_idade_escolar():
    return mommy.make(models.FaixaIdadeEscolar,
                      nome=fake.name())


@pytest.fixture
def codae(escola):
    return mommy.make(models.Codae,
                      make_m2m=True)


@pytest.fixture
def lote():
    return mommy.make(models.Lote)


@pytest.fixture
def periodo_escolar():
    return mommy.make(models.PeriodoEscolar)


@pytest.fixture
def sub_prefeitura():
    return mommy.make(models.Subprefeitura)
