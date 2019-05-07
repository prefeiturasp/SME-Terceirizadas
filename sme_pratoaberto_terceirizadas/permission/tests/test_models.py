import pytest

pytestmark = pytest.mark.django_db


def test_permission(permission, profile):
    assert permission.title == 'Mark Allen'
    assert permission.endpoint == 'https://www.stewart.com/'
    assert permission.permissions.all() == profile


def test_profile_permission(profile_permission):
    assert 1 == 1
