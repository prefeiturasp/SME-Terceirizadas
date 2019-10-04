import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

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
