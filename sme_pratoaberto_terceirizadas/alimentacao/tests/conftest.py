import pytest
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

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
def user():
    user = User.objects.all().first()
    return user
