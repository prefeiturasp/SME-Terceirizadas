import pytest
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings
from model_mommy import mommy
from django.utils.timezone import now

from sme_pratoaberto_terceirizadas.users.models import User

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def token():
    user = User.objects.all().first()
    paylod = jwt_payload_handler(user)
    token = jwt_encode_handler(paylod)
    return token


@pytest.fixture
def cardapio():
    user = mommy.prepare('users.User', _save_related=True)
    cardapio = mommy.prepare('Cardapio', _save_related=True, criado_em=now(), atualizado_por=user)
    return cardapio


@pytest.fixture
def inverter_dia_cardapio():
    inverter_dia_cardapio = mommy.prepare('InverterDiaCardapio', _save_related=True)
    return inverter_dia_cardapio


@pytest.fixture
def user():
    user = mommy.prepare('users.User', _save_related=True)
    return user


@pytest.fixture
def school():
    school = mommy.prepare('school.School', _save_related=True)
    return school
