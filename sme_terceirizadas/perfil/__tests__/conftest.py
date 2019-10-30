import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ..api.serializers import UsuarioSerializer, UsuarioUpdateSerializer

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


@pytest.fixture
def usuario_2():
    return mommy.make(
        models.Usuario,
        nome='Fulano da Silva',
        email='fulano@teste.com',
        cpf='11111111111',
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
                      content_type=models.ContentType.objects.get(model='diretoriaregional'))


@pytest.fixture
def usuario_update_serializer(usuario_2):
    return UsuarioUpdateSerializer(usuario_2)


@pytest.fixture(params=[
    ('admin_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000002'),
    ('admin_2@sme.prefeitura.sp.gov.br', 'xxASD123@@', '0000013'),
    ('admin_3@sme.prefeitura.sp.gov.br', '....!!!123213#$', '00440002'),
    ('admin_4@sme.prefeitura.sp.gov.br', 'XXXDDxx@@@77', '00000552'),
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
    ('diretor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('diretor_2@sme.prefeitura.sp.gov.br', 'aasdsadsadff', '0000002', '56789925031'),
    ('diretor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '000000123', '86880963099'),
    ('diretor_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('diretor_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0000005551', '40296233013')
])
def users_diretor_escola(client, django_user_model, request):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)

    escola = mommy.make('Escola', nome='Escola Teste', quantidade_alunos=420,
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_professor = mommy.make('Perfil', nome='Professor', ativo=False)
    perfil_diretor = mommy.make('Perfil', nome='Diretor', ativo=True)

    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor, ativo=False)
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor, ativo=True)

    return client, email, password, rf, cpf, user
