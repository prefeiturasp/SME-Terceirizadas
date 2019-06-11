import pytest

pytestmark = pytest.mark.django_db


def test_permission(permission):
    assert permission.title == 'Qui in ad placeat deserunt.'
    assert permission.endpoint == 'https://www.moura.org/'


def test_profile_permission(profile_permission):
    assert profile_permission.permission.title == 'Quidem vero occaecati iste delectus voluptate iure.'
    assert profile_permission.permission.endpoint == 'http://da.br/'
