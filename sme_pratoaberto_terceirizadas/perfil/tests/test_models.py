import pytest

pytestmark = pytest.mark.django_db


def test_perfil(perfil):
    assert perfil.nome == 'título do perfil'
    assert perfil.__str__() == 'título do perfil'
