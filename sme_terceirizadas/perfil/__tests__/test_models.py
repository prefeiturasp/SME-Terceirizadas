import datetime

import pytest
from django.db.utils import IntegrityError

from ..models import Perfil, Usuario

pytestmark = pytest.mark.django_db


def test_perfil(perfil):
    assert perfil.nome == 'título do perfil'
    assert perfil.__str__() == 'título do perfil'


def test_usuario(usuario):
    assert usuario.nome == 'Fulano da Silva'
    assert usuario.email == 'fulano@teste.com'
    assert usuario.tipo_usuario == 'indefinido'


def test_meta_modelo(perfil):
    assert perfil._meta.verbose_name == 'Perfil'
    assert perfil._meta.verbose_name_plural == 'Perfis'


def test_instance_model(perfil):
    assert isinstance(perfil, Perfil)


def test_vinculo(vinculo):
    assert (isinstance(vinculo.data_final, datetime.date) or vinculo.data_final is None)
    assert isinstance(vinculo.usuario, Usuario)
    assert isinstance(vinculo.perfil, Perfil)
    assert vinculo.status is vinculo.STATUS_ATIVO
    vinculo.finalizar_vinculo()
    assert vinculo.status is vinculo.STATUS_FINALIZADO
    assert vinculo.usuario.is_active is False
    assert vinculo.data_final is not None
    assert vinculo.ativo is False


def test_vinculo_aguardando_ativacao(vinculo_aguardando_ativacao):
    assert vinculo_aguardando_ativacao.status is vinculo_aguardando_ativacao.STATUS_AGUARDANDO_ATIVACAO


def test_vinculo_invalido(vinculo_invalido):
    with pytest.raises(IntegrityError, match='Status invalido'):
        vinculo_invalido.status


def test_vinculo_diretoria_regional(vinculo_diretoria_regional):
    assert vinculo_diretoria_regional.usuario.tipo_usuario == 'diretoriaregional'
