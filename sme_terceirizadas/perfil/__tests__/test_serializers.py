import pytest

from ..__tests__.conftest import mocked_request_api_eol
from ..api.serializers import UsuarioUpdateSerializer
from ..models import Usuario

pytestmark = pytest.mark.django_db


def test_usuario_serializer(usuario_serializer):
    assert usuario_serializer.data is not None


def test_usuario_update_serializer_partial_update(monkeypatch, usuario_update_serializer, usuario_2):
    dados_usuario = {
        'password': 'adminadmin',
        'confirmar_password': 'adminadmin',
        'email': 'nome.completo@sme.prefeitura.sp.gov.br',
        'registro_funcional': '1234567',
        'cpf': '11111111111'
    }
    monkeypatch.setattr(Usuario, 'pode_efetuar_cadastro', lambda: True)
    usuario = usuario_update_serializer.partial_update(usuario_2, dados_usuario)
    assert usuario.cpf == '11111111111'
    assert usuario.email == 'nome.completo@sme.prefeitura.sp.gov.br'
    assert usuario.registro_funcional == '1234567'


def test_usuario_update_serializer_create(monkeypatch):
    monkeypatch.setattr(UsuarioUpdateSerializer, 'get_informacoes_usuario',
                        lambda p1, p2: mocked_request_api_eol())
    data = {'registro_funcional': '5696569', 'instituicao': 'NOE AZEVEDO, PROF'}
    usuario = UsuarioUpdateSerializer(data).create(validated_data=data)
    assert isinstance(usuario, Usuario)
    assert usuario.registro_funcional == '5696569'
    assert usuario.is_active is False
    assert usuario.cpf == '95887745002'
