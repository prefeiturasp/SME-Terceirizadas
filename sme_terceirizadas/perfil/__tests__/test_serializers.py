import pytest

from ..models import Usuario

pytestmark = pytest.mark.django_db


def test_usuario_serializer(usuario_serializer):
    assert usuario_serializer.data is not None


def test_usuario_update_serializer(monkeypatch, usuario_update_serializer, usuario_2):
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
