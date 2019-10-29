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


@pytest.fixture
def vinculo_diretoria_regional(usuario):
    return mommy.make('Vinculo',
                      ativo=True,
                      usuario=usuario,
                      tipo_instituicao=models.ContentType.objects.get(model='diretoriaregional'))


@pytest.fixture(params=[
    ('admin_1@escola.com', 'adminadmin', '0000002'),
    ('admin_2@escola.com', 'xxASD123@@', '0000013'),
    ('admin_3@escola.com', '....!!!123213#$', '00440002'),
    ('admin_4@escola.com', 'XXXDDxx@@@77', '00000552'),
])
def users_admin_escola(client, django_user_model, request):
    email, password, rf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf)
    client.login(email=email, password=password)

    escola = mommy.make('Escola', nome='Escola Teste', quantidade_alunos=420,
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')
    perfil_professor = mommy.make('Perfil', nome='Professor', ativo=False)
    perfil_admin = mommy.make('Perfil', nome='Admin', ativo=True)

    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor, ativo=False)
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_admin, ativo=True)

    return client, email, password, rf, user


@pytest.fixture(params=[
    ('diretor_1@escola.com', 'adminadmin', '0000001'),
    ('diretor_2@escola.com', 'aasdsadsadff', '0000002'),
    ('diretor_3@escola.com', '98as7d@@#', '000000123'),
    ('diretor_4@escola.com', '##$$csazd@!', '0000441'),
    ('diretor_5@escola.com', '!!@##FFG121', '0000005551')
])
def users_diretor_escola(client, django_user_model, request):
    email, password, rf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf)
    client.login(email=email, password=password)

    escola = mommy.make('Escola', nome='Escola Teste', quantidade_alunos=420,
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_professor = mommy.make('Perfil', nome='Professor', ativo=False)
    perfil_diretor = mommy.make('Perfil', nome='Diretor', ativo=True)

    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor, ativo=False)
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor, ativo=True)

    return client, email, password, rf, user
