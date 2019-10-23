import pytest

pytestmark = pytest.mark.django_db


def test_perfil(perfil):
    assert perfil.nome == 'título do perfil'
    assert perfil.__str__() == 'título do perfil'


def test_usuario(usuario):
    assert usuario.nome == 'Fulano da Silva'
    assert usuario.email == 'fulano@teste.com'
