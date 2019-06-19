import pytest

pytestmark = pytest.mark.django_db


def test_permission(permissao):
    assert permissao.titulo == 'A permissão do fulano de tal'
    assert permissao.endpoint == 'http://meu.endpoint/'


def test_profile_permission(perfil_permissao):
    assert perfil_permissao.permissao.titulo == 'A permissão do fulano de tal'
    assert perfil_permissao.permissao.endpoint == 'http://meu.endpoint/'
