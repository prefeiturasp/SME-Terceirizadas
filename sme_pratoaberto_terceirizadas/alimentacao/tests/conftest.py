import pytest
from datetime import datetime
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings
from model_mommy import mommy
from django.utils.timezone import now

from sme_pratoaberto_terceirizadas.perfil.models import Usuario

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

FORMAT = '%Y-%m-%d'


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def token():
    user = Usuario.objects.all().first()
    paylod = jwt_payload_handler(user)
    token = jwt_encode_handler(paylod)
    return token


@pytest.fixture
def cardapio():
    user = mommy.prepare('perfil.User', _save_related=True)
    cardapio = mommy.prepare('Cardapio', _save_related=True, criado_em=now(), atualizado_por=user)
    return cardapio


@pytest.fixture
def inverter_dia_cardapio():
    inverter_dia_cardapio = mommy.prepare('InverterDiaCardapio', _save_related=True)
    return inverter_dia_cardapio


@pytest.fixture
def user():
    user = mommy.prepare('perfil.User', _save_related=True)
    return user


@pytest.fixture
def request_solicitar_errado():
    request = {
        "data_de": datetime(2019, 6, 10).date(),
        "data_para": datetime(2019, 6, 15).date(),
        "descricao": "Descrição para teste",
        "usuario": 1,
        "escola": 1
    }
    return request


@pytest.fixture
def request_solicitar_certo():
    request = {
        "data_de": datetime(2019, 6, 10).date(),
        "data_para": datetime(2019, 6, 14).date(),
        "descricao": "Descrição para teste",
        "usuario": 1,
        "escola": 1
    }
    return request


@pytest.fixture
def request_solicitar_feriado():
    request = {
        "data_de": datetime(2019, 6, 10).date(),
        "data_para": datetime(2019, 6, 20).date(),
        "descricao": "Descrição para teste",
        "usuario": 1,
        "escola": 1
    }
    return request


@pytest.fixture
def school():
    school = mommy.prepare('school.School', _save_related=True)
    return school


@pytest.fixture
def request_post():
    request = {
        "data_de": datetime(2019, 6, 13),
        "data_para": datetime(2019, 6, 20),
        "descricao": "Descrição para teste",
        "usuario": mommy.prepare('perfil.User', _save_related=True),
        "escola": mommy.prepare('School', _save_related=True)
    }
    return request


@pytest.fixture
def usuario_sem_escola():
    usuario = mommy.prepare('perfil.User', _save_related=True)
    return usuario
