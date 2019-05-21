from rest_framework.test import APITestCase
from rest_framework import status
from django.test import RequestFactory
from django.urls import reverse, resolve
import pytest

pytestmark = pytest.mark.django_db


class TestUrls(APITestCase):

    def test_meal_kit_endpoint(self):
        request = RequestFactory()
        response = self.client.get('/kit-lanche/')
        assert response.status_code, status.HTTP_401_UNAUTHORIZED




