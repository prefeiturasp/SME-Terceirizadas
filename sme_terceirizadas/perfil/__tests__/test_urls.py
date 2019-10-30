import pytest
from rest_framework import status

from ..api.viewsets import UsuarioUpdateViewSet
from ..models import Usuario

pytestmark = pytest.mark.django_db


def test_get_usuarios(client_autenticado):
    response = client_autenticado.get('/usuarios/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    json = response.json()
    assert json['count'] == 1
    assert json['results'][0]['email'] == 'test@test.com'


def test_get_meus_dados_admin_escola(users_admin_escola):
    client, email, password, rf, user = users_admin_escola
    response = client.get('/usuarios/meus-dados/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    json = response.json()
    keys = ['uuid', 'nome', 'email', 'registro_funcional', 'date_joined', 'vinculo_atual', 'tipo_usuario']
    for key in keys:
        assert key in json.keys()
    assert json['email'] == email
    assert json['registro_funcional'] == rf
    assert json['tipo_usuario'] == 'escola'
    assert json['vinculo_atual'] == {
        'instituicao': {'nome': 'Escola Teste', 'uuid': 'b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd',
                        'quantidade_alunos': 420}, 'lotes': {'lotes': []}}
    assert user.vinculo_atual.perfil.nome == 'Admin'


def test_get_meus_dados_diretor_escola(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    response = client.get('/usuarios/meus-dados/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    json = response.json()
    keys = ['uuid', 'nome', 'email', 'registro_funcional', 'date_joined', 'vinculo_atual', 'tipo_usuario']
    for key in keys:
        assert key in json.keys()
    assert json['email'] == email
    assert json['registro_funcional'] == rf
    assert json['tipo_usuario'] == 'escola'
    assert json['vinculo_atual'] == {
        'instituicao': {'nome': 'Escola Teste', 'uuid': 'b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd',
                        'quantidade_alunos': 420}, 'lotes': {'lotes': []}}
    assert user.vinculo_atual.perfil.nome == 'Diretor'


def test_cadastro_erro(client):
    response = client.post('/cadastro/', data={
        'email': 'string',
        'registro_funcional': 'string',
        'password': 'string',
        'confirmar_password': 'string',
        'cpf': 'string'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.json(), dict)
    assert response.json() == {
        'detail': 'Erro ao cadastrar usuário'
    }


def test_cadastro_diretor(client, users_diretor_escola, monkeypatch):
    _, email, password, rf, cpf, user = users_diretor_escola
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        'email': email,
        'registro_funcional': rf,
        'password': password,
        'confirmar_password': password,
        'cpf': cpf
    }
    assert user.registro_funcional == rf

    monkeypatch.setattr(UsuarioUpdateViewSet, '_get_usuario', lambda p1, p2: user)
    monkeypatch.setattr(Usuario, 'pode_efetuar_cadastro',
                        lambda: True)
    response = client.post('/cadastro/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    keys = ['uuid', 'nome', 'email', 'registro_funcional', 'date_joined', 'vinculo_atual', 'tipo_usuario']
    for key in keys:
        assert key in json.keys()
    assert json['email'] == email
    assert json['registro_funcional'] == rf
    assert json['tipo_usuario'] == 'escola'
    assert json['vinculo_atual'] == {
        'instituicao': {'nome': 'Escola Teste', 'uuid': 'b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd',
                        'quantidade_alunos': 420}, 'lotes': {'lotes': []}}


def test_post_usuarios(client_autenticado):
    response = client_autenticado.post('/usuarios/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    response = client_autenticado.put('/usuarios/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
