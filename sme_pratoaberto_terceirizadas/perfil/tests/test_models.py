import pytest

pytestmark = pytest.mark.django_db


def test_profile(profile):
    assert profile.title == 'título do perfil'
    assert profile.__str__() == 'título do perfil'
    assert profile.institution.name == 'Faker SA'
    assert profile.institution.__str__() == 'Faker SA'
