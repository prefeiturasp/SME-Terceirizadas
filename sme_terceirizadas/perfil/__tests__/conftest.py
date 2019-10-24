import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ..api.serializers import UsuarioSerializer

f = Faker(locale='pt-Br')


@pytest.fixture
def perfil():
    return mommy.make(models.Perfil, nome='título do perfil')


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


@pytest.fixture
def vinculo(perfil, usuario):
    return mommy.make('Vinculo', perfil=perfil, usuario=usuario)
