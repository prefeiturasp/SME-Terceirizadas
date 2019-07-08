import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

f = Faker(locale='pt-Br')


@pytest.fixture
def perfil():
    permissoes = mommy.make(models.Permissao, nome=f.name(), _quantity=4)
    grupo = mommy.make(models.GrupoPerfil, nome=f.name(), descricao=f.text())
    return mommy.make(models.Perfil, nome='título do perfil',
                      permissoes=permissoes, grupo=grupo)


@pytest.fixture
def permissao():
    return mommy.make(models.Permissao, nome='pode dar aula')


@pytest.fixture
def grupo_perfil():
    return mommy.make(models.GrupoPerfil, nome='Diretoria XYZ',
                      descricao='Esse grupo é de diretores...')
