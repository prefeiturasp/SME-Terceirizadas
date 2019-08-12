from datetime import datetime, timedelta

import pytest
from faker import Faker
from model_mommy import mommy
from rest_framework.test import APIClient

from ..models import (
    Edital,
    Contrato,
    VigenciaContrato,
    Terceirizada
)

from ..api.serializers.serializers import (
    VigenciaContratoSerializer,
    ContratoSerializer,
    EditalContratosSerializer,
    TerceirizadaSimplesSerializer
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

@pytest.fixture
def vigencia_contrato_serializer():
    vigencia_contrato = mommy.make(VigenciaContrato)
    return VigenciaContratoSerializer(vigencia_contrato)

@pytest.fixture
def contrato_serializer():
    contrato = mommy.make(Contrato)
    return ContratoSerializer(contrato)


@pytest.fixture
def edital_contratos_serializer():
    edital_contratos = mommy.make(Edital)
    return EditalContratosSerializer(edital_contratos)


@pytest.fixture
def terceirizada_simples_serializer():
    terceirizada = mommy.make(Terceirizada)
    return TerceirizadaSimplesSerializer(terceirizada)
