import datetime

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
def escola():
    return mommy.make('Escola', nome='EscolaTeste', quantidade_alunos=421)


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
def usuario_2(escola):
    return mommy.make(
        models.Usuario,
        nome='Fulano da Silva',
        email='fulano@teste.com',
        cpf='11111111111',
        registro_funcional='1234567'
    )


@pytest.fixture()
def usuario_com_rf_de_diretor(escola):
    hoje = datetime.date.today()
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    user = mommy.make(
        models.Usuario,
        registro_funcional='6580157'
    )
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, data_final=None, ativo=True)  # ativo
    return user


@pytest.fixture
def usuario_serializer(usuario):
    return UsuarioSerializer(usuario)


@pytest.fixture
def vinculo(perfil, usuario):
    hoje = datetime.date.today()
    return mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=hoje,
                      data_final=None, ativo=True)


@pytest.fixture
def vinculo_aguardando_ativacao(perfil, usuario):
    return mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=None,
                      data_final=None, ativo=False)


@pytest.fixture(params=[
    # dataini, datafim, ativo
    (datetime.date(2000, 1, 12), datetime.date(2000, 1, 12), True),  # nao pode data final e ativo
    (None, datetime.date(2000, 1, 12), True),  # nao pode data final sem data inicial
    (None, datetime.date(2000, 1, 12), False),  # nao pode data final sem data inicial,
    (datetime.date(2000, 1, 12), None, False)  # nao pode data inicio, sem data fim e inativo
])
def vinculo_invalido(perfil, usuario, request):
    dataini, datafim, ativo = request.param
    return mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=dataini,
                      data_final=datafim, ativo=ativo)


@pytest.fixture
def vinculo_diretoria_regional(usuario):
    return mommy.make('Vinculo',
                      data_inicial=datetime.date.today(),
                      ativo=True,
                      usuario=usuario,
                      content_type=models.ContentType.objects.get(model='diretoriaregional'))


@pytest.fixture
def usuario_update_serializer(usuario_2):
    return UsuarioUpdateSerializer(usuario_2)


@pytest.fixture(params=[
    ('admin_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000002'),
    ('admin_2@sme.prefeitura.sp.gov.br', 'xxASD123@@', '0000013'),
    ('admin_3@sme.prefeitura.sp.gov.br', '....!!!123213#$', '0044002'),
    ('admin_4@sme.prefeitura.sp.gov.br', 'XXXDDxx@@@77', '0000552'),
])
def users_admin_escola(client, django_user_model, request):
    email, password, rf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf)
    client.login(email=email, password=password)

    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF', quantidade_alunos=420,
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')
    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_ESCOLA', ativo=False)
    perfil_admin = mommy.make('Perfil', nome='Admin', ativo=True, uuid='d6fd15cc-52c6-4db4-b604-018d22eeb3dd')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor,
               data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30), ativo=False)  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_admin,
               data_inicial=hoje, ativo=True)  # ativo

    return client, email, password, rf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('diretor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('diretor_2@sme.prefeitura.sp.gov.br', 'aasdsadsadff', '0000002', '56789925031'),
    ('diretor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('diretor_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('diretor_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0005551', '40296233013')
])
def users_diretor_escola(client, django_user_model, request):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)

    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF', quantidade_alunos=420,
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_ESCOLA', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)

    return client, email, password, rf, cpf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('cogestor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('cogestor_2@sme.prefeitura.sp.gov.br', 'aasdsadsadff', '0000002', '56789925031'),
    ('cogestor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('cogestor_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('cogestor_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0005551', '40296233013')
])
def users_cogestor_diretoria_regional(client, django_user_model, request):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)

    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO',
                                    uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_DRE', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_cogestor = mommy.make('Perfil', nome='COGESTOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=diretoria_regional, perfil=perfil_professor,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=diretoria_regional, perfil=perfil_cogestor,
               data_inicial=hoje, ativo=True)

    return client, email, password, rf, cpf, user


def mocked_request_api_eol():
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({'results': [{'nm_pessoa': 'IARA DAREZZO', 'cargo': 'PROF.ED.INF.E ENS.FUND.I',
                                      'divisao': 'ODILIO DENYS, MAL.',
                                      'cd_cpf_pessoa': '95887745002',
                                      'coord': 'DIRETORIA REGIONAL DE EDUCACAO FREGUESIA/BRASILANDIA'},
                                     {'nm_pessoa': 'IARA DAREZZO',
                                      'cargo': 'PROF.ENS.FUND.II E MED.-PORTUGUES',
                                      'divisao': 'NOE AZEVEDO, PROF',
                                      'cd_cpf_pessoa': '95887745002',
                                      'coord': 'DIRETORIA REGIONAL DE EDUCACAO JACANA/TREMEMBE'}]}, 200)


def mocked_request_api_eol_usuario_diretoria_regional():
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({'results': [{'nm_pessoa': 'LUIZA MARIA BASTOS', 'cargo': 'AUXILIAR TECNICO DE EDUCACAO',
                                      'divisao': 'DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO',
                                      'cd_cpf_pessoa': '47088910080',
                                      'coord': 'DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO'}]}, 200)


@pytest.fixture(params=[
    # nome, uuid
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),

])
def usuarios_pendentes_confirmacao(request, perfil, escola):
    nome, uuid = request.param
    usuario = mommy.make('Usuario', nome=nome, uuid=uuid, is_active=False)
    hoje = datetime.date.today()
    mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=None, data_final=None, ativo=False,
               instituicao=escola)  # vinculo esperando ativacao

    mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=hoje,
               data_final=hoje + datetime.timedelta(days=100), ativo=False,
               instituicao=escola)  # vinculo finalizado

    return usuario


@pytest.fixture(params=[
    # email, esprado
    ('tebohelleb-2297@sme.prefeitura.gov.br', 't*************7@sme.prefeitura.gov.br'),
    ('surracecyss-9018@sme.prefeitura.gov.br', 's**************8@sme.prefeitura.gov.br'),
    ('zoffexupi-7784@sme.prefeitura.gov.br', 'z************4@sme.prefeitura.gov.br'),
    ('fulano157@sme.prefeitura.gov.br', 'f*******7@sme.prefeitura.gov.br')
])
def email_list(request):
    return request.param
