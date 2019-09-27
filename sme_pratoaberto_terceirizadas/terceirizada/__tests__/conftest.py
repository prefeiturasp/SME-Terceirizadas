import pytest
from faker import Faker
from model_mommy import mommy
from rest_framework.test import APIClient

from ..api.serializers.serializers import (
    ContratoSerializer, EditalContratosSerializer, TerceirizadaSimplesSerializer, VigenciaContratoSerializer
)
from ..models import (
    Contrato, Edital, Nutricionista, Terceirizada, VigenciaContrato
)

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def client_autenticado_terceiro(client_autenticado,):
    terceirizada = mommy.make(Terceirizada,
                              usuarios=[mommy.make('perfil.Usuario')],
                              contatos=[mommy.make('dados_comuns.Contato')],
                              endereco=mommy.make('dados_comuns.Endereco'),
                              make_m2m=True
                              )

    mommy.make(Nutricionista,
               terceirizada=terceirizada,
               contatos=[mommy.make('dados_comuns.Contato')],
               )
    mommy.make(Contrato, terceirizada=terceirizada, edital=mommy.make(Edital), make_m2m=True)
    return client_autenticado


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
