import pytest

pytestmark = pytest.mark.django_db


def test_permission(permission):
    assert permission.title == 'A permissão do fulano de tal'
    assert permission.endpoint == 'http://meu.endpoint/'


def test_profile_permission(profile_permission):
    assert profile_permission.permission.title == 'A permissão do fulano de tal'
    assert profile_permission.permission.endpoint == 'http://meu.endpoint/'
