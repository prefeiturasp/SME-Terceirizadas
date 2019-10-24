import datetime

import pytest

from ..models import Perfil, Usuario

pytestmark = pytest.mark.django_db


def test_perfil(perfil):
    assert perfil.nome == 'título do perfil'
    assert perfil.__str__() == 'título do perfil'


def test_usuario(usuario):
    assert usuario.nome == 'Fulano da Silva'
    assert usuario.email == 'fulano@teste.com'


def test_vinculo(vinculo):
    assert isinstance(vinculo.data_inicial, datetime.date)
    assert (isinstance(vinculo.data_final, datetime.date) or vinculo.data_final is None)
    assert isinstance(vinculo.usuario, Usuario)
    assert isinstance(vinculo.perfil, Perfil)
