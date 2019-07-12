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
    cardapio_valido = mommy.prepare('Cardapio', _save_related=True, id=1, data=datetime(2019, 7, 18).date(),
                                    uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4b')
    return cardapio_valido


@pytest.fixture
def cardapio_valido2():
    cardapio_valido2 = mommy.prepare('Cardapio', _save_related=True, id=2, data=datetime(2019, 7, 19).date(),
                                     uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4c')
    return cardapio_valido2


@pytest.fixture
def cardapio_invalido():
    cardapio_invalido = mommy.prepare('Cardapio', _save_related=True, id=3, data=datetime(2019, 7, 2).date(),
                                      uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4d')
    return cardapio_invalido


@pytest.fixture
def escola():
    escola = mommy.prepare('Escola', _save_related=True)
    return escola
