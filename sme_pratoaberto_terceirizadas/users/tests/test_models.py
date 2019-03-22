import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: settings.AUTH_USER_MODEL):
    assert user.get_absolute_url() == f"/users/{user.username}/"


def test_new_user(django_user_model):
    django_user_model.objects.create(username="someone", is_nutritionist=True, functional_register="etc",
                                     password="something", phone='phone', mobile_phone='mob')
