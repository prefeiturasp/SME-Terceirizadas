import pytest

pytestmark = pytest.mark.django_db


def test_permission(permission):
    assert 2 == 2


def test_profile_permission(profile_permission):
    assert 1 == 1
