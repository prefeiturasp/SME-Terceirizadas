import datetime

import pytest
from faker import Faker
from model_mommy import mommy
from rest_framework import status

import sme_terceirizadas.escola.models as models

pytestmark = pytest.mark.django_db

fake = Faker('pt_BR')
Faker.seed(420)


@pytest.fixture
def tipo_gestao():
    return mommy.make(models.TipoGestao,
                      nome=fake.name())


@pytest.fixture
def lote():
    return mommy.make(models.Lote, nome='lote', iniciais='lt')


@pytest.fixture
def periodo_escolar():
    return mommy.make(models.PeriodoEscolar, nome='TARDE')


@pytest.fixture
def escola(lote, tipo_gestao):
    return mommy.make(models.Escola,
                      nome=fake.name(),
                      codigo_eol=fake.name()[:6],
                      lote=lote,
                      tipo_gestao=tipo_gestao)


@pytest.fixture
def aluno(escola, periodo_escolar):
    return mommy.make(models.Aluno,
                      nome='Fulano da Silva',
                      codigo_eol='000001',
                      data_nascimento=datetime.date(2000, 1, 1),
                      escola=escola,
                      periodo_escolar=periodo_escolar)


def test_consultar_dados_aluno(client_autenticado, aluno, escola):
    response = client_autenticado.get(
        f'/dados-alunos-eol/{aluno.codigo_eol}/'
    )
    assert response.status_code == status.HTTP_200_OK
