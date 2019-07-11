import pytest
from datetime import datetime
from model_mommy import mommy
from rest_framework.test import APIClient


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def cardapio_valido():
    return '7a4ec98a-18a8-4d0a-b722-1da8f99aaf4b'


@pytest.fixture
def cardapio_invalido():
    return '7c0ebc5b-5a2d-4541-993d-b1650648f5d7'
