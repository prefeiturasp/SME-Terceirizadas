import pytest

pytestmark = pytest.mark.django_db


def test_permission(permission, profile):
    assert permission.title == 'Art therapist'
    assert permission.endpoint == 'https://www.smith.org/'


def test_profile_permission(profile_permission):
    assert profile_permission.permission.title == 'Television floor manager'
