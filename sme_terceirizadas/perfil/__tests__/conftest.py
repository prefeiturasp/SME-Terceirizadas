import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ..api.serializers import UsuarioSerializer

f = Faker(locale='pt-Br')


@pytest.fixture
def perfil():
    grupo = mommy.make(models.GrupoPerfil, nome=f.name(), descricao=f.text())
    return mommy.make(models.Perfil, nome='título do perfil', grupo=grupo)


@pytest.fixture
def permissao():
    return mommy.make(models.Permissao, nome='pode dar aula')


@pytest.fixture
def grupo_perfil():
    return mommy.make(models.GrupoPerfil, nome='Diretoria XYZ',
                      descricao='Esse grupo é de diretores...')


@pytest.fixture
def usuario():
    return mommy.make(
        models.Usuario,
        nome='Fulano da Silva',
        email='fulano@teste.com',
        cpf='52347255100',
        registro_funcional='1234567'
    )


@pytest.fixture()
def usuario_com_rf_de_diretor():
    return mommy.make(
        models.Usuario,
        registro_funcional='6580157'
    )


@pytest.fixture
def usuario_serializer(usuario):
    return UsuarioSerializer(usuario)
