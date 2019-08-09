from datetime import datetime, timedelta

import pytest
from faker import Faker
from model_mommy import mommy
from rest_framework.test import APIClient

from sme_pratoaberto_terceirizadas.dados_comuns.models import TemplateMensagem

from ..models import (
    Edital,
    Contrato,
    VigenciaContrato
)

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def client():
    client = APIClient()
    return client

@pytest.fixture
def edital():
    return mommy.make(Edital)

@pytest.fixture
def contrato():
    return mommy.make(Contrato)

@pytest.fixture
def vigencia_contrato():
    return mommy.make(VigenciaContrato)
