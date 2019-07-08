import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    client = APIClient()
    return client
