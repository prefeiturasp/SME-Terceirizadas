import pytest

pytestmark = pytest.mark.django_db


def test_perfil(perfil):
    assert perfil.nome == 'título do perfil'
    assert perfil.__str__() == 'título do perfil'
    assert perfil.grupo is not None


def test_permissao(permissao):
    assert permissao.nome == 'pode dar aula'
    assert permissao.__str__() == 'pode dar aula'


def test_grupo_perfil(grupo_perfil):
    assert grupo_perfil.descricao == 'Esse grupo é de diretores...'
    assert grupo_perfil.nome == 'Diretoria XYZ'
    assert grupo_perfil.__str__() == 'Diretoria XYZ'


def test_usuario(usuario):
    assert usuario.nome == 'Fulano da Silva'
    assert usuario.email == 'fulano@teste.com'
    assert usuario.tipo_usuario == 'indefinido'
