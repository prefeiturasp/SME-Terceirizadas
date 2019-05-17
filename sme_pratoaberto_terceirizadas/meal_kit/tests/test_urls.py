from rest_framework.test import APITestCase
from rest_framework import status
import pytest

pytestmark = pytest.mark.django_db


class TestUrls(APITestCase):

    def test_meal_kit_endpoint(self):
        response = self.client.get('/kit-lanche/')

        assert response.status_code, status.HTTP_200_OK
