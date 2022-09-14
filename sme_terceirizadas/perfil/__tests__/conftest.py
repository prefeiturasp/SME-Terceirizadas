import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from ...dados_comuns.constants import DJANGO_ADMIN_PASSWORD
from .. import models
from ..api.serializers import UsuarioSerializer, UsuarioUpdateSerializer

f = Faker(locale='pt-Br')


@pytest.fixture
def perfil():
    return mommy.make(models.Perfil, nome='título do perfil', uuid='d38e10da-c5e3-4dd5-9916-010fc250595a')


@pytest.fixture
def escola():
    return mommy.make('Escola', nome='EscolaTeste', uuid='230453bb-d6f1-4513-b638-8d6d150d1ac6')


@pytest.fixture
def diretoria_regional():
    return mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL DE EDUCACAO ITAQUERA',
                      uuid='7bb20934-e740-4621-a906-bccb8ea98414')


@pytest.fixture
def codae(escola):
    return mommy.make('Codae',
                      make_m2m=True)


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
        uuid='8344f23a-95c4-4871-8f20-3880529767c0',
        nome='Fulano da Silva',
        email='fulano@teste.com',
        cpf='11111111111',
        registro_funcional='1234567'
    )


@pytest.fixture
def usuario_3():
    user = mommy.make(
        models.Usuario,
        uuid='155743d3-b16d-4899-8224-efc694053055',
        nome='Siclano Souza',
        email='siclano@teste.com',
        cpf='22222222222',
        registro_funcional='7654321'
    )
    mommy.make(
        'Vinculo',
        usuario=user,
        perfil=mommy.make('Perfil'),
        ativo=True,
        data_inicial=datetime.date.today(),
        data_final=None
    )
    return user


@pytest.fixture()
def usuario_com_rf_de_diretor(escola):
    hoje = datetime.date.today()
    perfil_diretor = mommy.make(
        'Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
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
    (datetime.date(2000, 1, 12), datetime.date(
        2000, 1, 12), True),  # nao pode data final e ativo
    # nao pode data final sem data inicial
    (None, datetime.date(2000, 1, 12), True),
    # nao pode data final sem data inicial,
    (None, datetime.date(2000, 1, 12), False),
    # nao pode data inicio, sem data fim e inativo
    (datetime.date(2000, 1, 12), None, False)
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


@pytest.fixture
def tipo_gestao():
    return mommy.make('TipoGestao', nome='TERC TOTAL')


@pytest.fixture(params=[
    ('admin_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000002'),
    ('admin_2@sme.prefeitura.sp.gov.br', 'xxASD123@@', '0000013'),
    ('admin_3@sme.prefeitura.sp.gov.br', '....!!!123213#$', '0044002'),
    ('admin_4@sme.prefeitura.sp.gov.br', 'XXXDDxx@@@77', '0000552'),
])
def users_admin_escola(client, django_user_model, request, tipo_gestao):
    email, password, rf = request.param
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional=rf)
    client.login(username=email, password=password)

    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad', codigo_eol=987656)
    cardapio1 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 15))
    tipo_unidade_escolar = mommy.make('escola.TipoUnidadeEscolar',
                                      iniciais=f.name()[:10],
                                      cardapios=[cardapio1, cardapio2],
                                      uuid='56725de5-89d3-4edf-8633-3e0b5c99e9d4')
    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF',
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd', diretoria_regional=diretoria_regional,
                        codigo_eol='256341', tipo_unidade=tipo_unidade_escolar, tipo_gestao=tipo_gestao)
    periodo_escolar_tarde = mommy.make(
        'PeriodoEscolar', nome='TARDE', uuid='57af972c-938f-4f6f-9f4b-cf7b983a10b7')
    periodo_escolar_manha = mommy.make(
        'PeriodoEscolar', nome='MANHA', uuid='d0c12dae-a215-41f6-af86-b7cd1838ba81')
    mommy.make('EscolaPeriodoEscolar', escola=escola,
               quantidade_alunos=230, periodo_escolar=periodo_escolar_tarde)
    mommy.make('EscolaPeriodoEscolar', escola=escola,
               quantidade_alunos=220, periodo_escolar=periodo_escolar_manha)
    perfil_professor = mommy.make(
        'Perfil', nome='ADMINISTRADOR_ESCOLA', ativo=False)
    perfil_admin = mommy.make(
        'Perfil', nome='Admin', ativo=True, uuid='d6fd15cc-52c6-4db4-b604-018d22eeb3dd')
    hoje = datetime.date.today()

    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor,
               data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30), ativo=False)  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_admin,
               data_inicial=hoje, ativo=True)  # ativo

    return client, email, password, rf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('diretor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('diretor_2@sme.prefeitura.sp.gov.br',
     'aasdsadsadff', '0000002', '56789925031'),
    ('diretor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('diretor_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('diretor_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0005551', '40296233013')
])
def users_diretor_escola(client, django_user_model, request, usuario_2, tipo_gestao):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional=rf, cpf=cpf)
    client.login(username=email, password=password)

    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad', codigo_eol=987656)
    cardapio1 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 15))
    tipo_unidade_escolar = mommy.make('escola.TipoUnidadeEscolar',
                                      iniciais='EMEF',
                                      cardapios=[cardapio1, cardapio2],
                                      uuid='56725de5-89d3-4edf-8633-3e0b5c99e9d4')
    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF',
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd', diretoria_regional=diretoria_regional,
                        codigo_eol='256341', tipo_unidade=tipo_unidade_escolar, tipo_gestao=tipo_gestao)
    periodo_escolar_tarde = mommy.make(
        'PeriodoEscolar', nome='TARDE', uuid='57af972c-938f-4f6f-9f4b-cf7b983a10b7')
    periodo_escolar_manha = mommy.make(
        'PeriodoEscolar', nome='MANHA', uuid='d0c12dae-a215-41f6-af86-b7cd1838ba81')
    mommy.make('EscolaPeriodoEscolar', escola=escola,
               quantidade_alunos=230, periodo_escolar=periodo_escolar_tarde)
    mommy.make('EscolaPeriodoEscolar', escola=escola,
               quantidade_alunos=220, periodo_escolar=periodo_escolar_manha)
    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_ESCOLA', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_diretor = mommy.make(
        'Perfil', nome='COORDENADOR_ESCOLA', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    mommy.make('Vinculo', usuario=usuario_2, instituicao=escola, perfil=perfil_professor,
               data_inicial=hoje, ativo=True)
    return client, email, password, rf, cpf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('cogestor_1@sme.prefeitura.sp.gov.br',
     'adminadmin', '0000001', '44426575052'),
    ('cogestor_2@sme.prefeitura.sp.gov.br',
     'aasdsadsadff', '0000002', '56789925031'),
    ('cogestor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('cogestor_4@sme.prefeitura.sp.gov.br',
     '##$$csazd@!', '0000441', '13151715036'),
    ('cogestor_5@sme.prefeitura.sp.gov.br',
     '!!@##FFG121', '0005551', '40296233013')
])
def users_cogestor_diretoria_regional(client, django_user_model, request, usuario_2):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional=rf, cpf=cpf)
    client.login(username=email, password=password)

    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO',
                                    uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_DRE', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_cogestor = mommy.make(
        'Perfil', nome='COGESTOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=diretoria_regional, perfil=perfil_professor,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=diretoria_regional, perfil=perfil_cogestor,
               data_inicial=hoje, ativo=True)
    mommy.make('Vinculo', usuario=usuario_2, instituicao=diretoria_regional, perfil=perfil_professor,
               data_inicial=hoje, ativo=True)

    return client, email, password, rf, cpf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('cogestor_1@sme.prefeitura.sp.gov.br',
     'adminadmin', '0000001', '44426575052'),
    ('cogestor_2@sme.prefeitura.sp.gov.br',
     'aasdsadsadff', '0000002', '56789925031'),
    ('cogestor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('cogestor_4@sme.prefeitura.sp.gov.br',
     '##$$csazd@!', '0000441', '13151715036'),
    ('cogestor_5@sme.prefeitura.sp.gov.br',
     '!!@##FFG121', '0005551', '40296233013')
])
def users_codae_gestao_alimentacao(client, django_user_model, request, usuario_2):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional=rf, cpf=cpf)
    client.login(username=email, password=password)

    codae = mommy.make('Codae', nome='CODAE',
                       uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_administrador_codae = mommy.make('Perfil', nome='ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA', ativo=True,
                                            uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_coordenador = mommy.make('Perfil', nome='COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA', ativo=True,
                                    uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_administrador_codae,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_coordenador,
               data_inicial=hoje, ativo=True)
    mommy.make('Vinculo', usuario=usuario_2, instituicao=codae, perfil=perfil_administrador_codae,
               data_inicial=hoje, ativo=True)

    return client, email, password, rf, cpf, user


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('cogestor_1@sme.prefeitura.sp.gov.br',
     'adminadmin', '0000001', '44426575052'),
    ('cogestor_2@sme.prefeitura.sp.gov.br',
     'aasdsadsadff', '0000002', '56789925031'),
    ('cogestor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('cogestor_4@sme.prefeitura.sp.gov.br',
     '##$$csazd@!', '0000441', '13151715036'),
    ('cogestor_5@sme.prefeitura.sp.gov.br',
     '!!@##FFG121', '0005551', '40296233013')
])
def users_terceirizada(client, django_user_model, request, usuario_2):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional=rf, cpf=cpf)
    client.login(username=email, password=password)
    mommy.make('Codae')
    terceirizada = mommy.make('Terceirizada', nome_fantasia='Alimentos LTDA',
                              uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_nutri_admin_responsavel = mommy.make('Perfil', nome='NUTRI_ADMIN_RESPONSAVEL', ativo=True,
                                                uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_administrador_terceirizada = mommy.make('Perfil', nome='ADMINISTRADOR_TERCEIRIZADA',
                                                   ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=terceirizada, perfil=perfil_administrador_terceirizada,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=terceirizada, perfil=perfil_nutri_admin_responsavel,
               data_inicial=hoje, ativo=True)
    mommy.make('Vinculo', usuario=usuario_2, instituicao=terceirizada, perfil=perfil_administrador_terceirizada,
               data_inicial=hoje, ativo=True)

    return client, email, password, rf, cpf, user


def mocked_request_api_eol():
    return [{'nm_pessoa': 'IARA DAREZZO', 'cargo': 'PROF.ED.INF.E ENS.FUND.I',
             'divisao': 'ODILIO DENYS, MAL.',
             'cd_cpf_pessoa': '95887745002',
             'coord': 'DIRETORIA REGIONAL DE EDUCACAO FREGUESIA/BRASILANDIA'},
            {'nm_pessoa': 'IARA DAREZZO',
             'cargo': 'PROF.ENS.FUND.II E MED.-PORTUGUES',
             'divisao': 'NOE AZEVEDO, PROF',
             'cd_cpf_pessoa': '95887745002',
             'coord': 'DIRETORIA REGIONAL DE EDUCACAO JACANA/TREMEMBE'}]


def mocked_request_api_eol_usuario_diretoria_regional():
    return [{'nm_pessoa': 'LUIZA MARIA BASTOS', 'cargo': 'AUXILIAR TECNICO DE EDUCACAO',
             'divisao': 'DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO',
             'cd_cpf_pessoa': '47088910080',
             'coord': 'DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO'}]


@pytest.fixture(params=[
    # nome, uuid
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),
    (f.name(), f.uuid4()),

])
def usuarios_pendentes_confirmacao(request, perfil, tipo_gestao):
    nome = 'Bruno da Conceição'
    uuid = 'd36fa08e-e91e-4acb-9d54-b88115147e8e'
    usuario = mommy.make('Usuario', nome=nome, uuid=uuid, username='1234567',
                         is_active=False, registro_funcional='1234567', email='GrVdXIhxqb@example.com')
    hoje = datetime.date.today()

    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad', codigo_eol=987656)
    cardapio1 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio',
                           data=datetime.date(2019, 10, 15))
    tipo_unidade_escolar = mommy.make('escola.TipoUnidadeEscolar',
                                      iniciais='EMEF',
                                      cardapios=[cardapio1, cardapio2],
                                      uuid='56725de5-89d3-4edf-8633-3e0b5c99e9d4')
    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF',
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd', diretoria_regional=diretoria_regional,
                        codigo_eol='256341', tipo_unidade=tipo_unidade_escolar, tipo_gestao=tipo_gestao)

    mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=None, data_final=None, ativo=False,
               instituicao=escola)  # vinculo esperando ativacao

    mommy.make('Vinculo', perfil=perfil, usuario=usuario, data_inicial=hoje,
               data_final=hoje + datetime.timedelta(days=100), ativo=False,
               instituicao=escola)  # vinculo finalizado

    return usuario


@pytest.fixture(params=[
    # email, esprado
    ('tebohelleb-2297@sme.prefeitura.sp.gov.br', 't*************7@sme.prefeitura.sp.gov.br'),
    ('surracecyss-9018@sme.prefeitura.sp.gov.br', 's**************8@sme.prefeitura.sp.gov.br'),
    ('zoffexupi-7784@sme.prefeitura.sp.gov.br', 'z************4@sme.prefeitura.sp.gov.br'),
    ('fulano157@sme.prefeitura.sp.gov.br', 'f*******7@sme.prefeitura.sp.gov.br'),
    ('tebohelleb-2297@prefeitura.sp.gov.br', 't*************7@prefeitura.sp.gov.br'),
    ('surracecyss-9018@prefeitura.sp.gov.br', 's**************8@prefeitura.sp.gov.br'),
    ('zoffexupi-7784@prefeitura.sp.gov.br', 'z************4@prefeitura.sp.gov.br'),
    ('fulano157@prefeitura.sp.gov.br', 'f*******7@prefeitura.sp.gov.br')
])
def email_list(request):
    return request.param


@pytest.fixture(params=[
    # email, esprado
    ('tebohelleb-2297@smea.prefeitura.sp.gov.br', 't*************7@sme.prefeitura.sp.gov.br'),
    ('surracecyss-9018@smes.prefeitura.sp.gov.br', 's**************8@sme.prefeitura.sp.gov.br'),
    ('zoffexupi-7784@smed.prefeitura.sp.gov.br', 'z************4@sme.prefeitura.sp.gov.br'),
    ('fulano157@smea.prefeitura.sp.gov.br', 'f*******7@sme.prefeitura.sp.gov.br'),
    ('tebohelleb-2297@prefeituraa.sp.gov.br', 't*************7@prefeiturab.sp.gov.br'),
    ('surracecyss-9018@prefeiturab.sp.gov.br', 's**************8@prefeiturac.sp.gov.br'),
    ('zoffexupi-7784@prefeiturac.sp.gov.br', 'z************4@prefeiturad.sp.gov.br'),
    ('fulano157@prefeiturad.sp.gov.br', 'f*******7@prefeiturae.sp.gov.br')
])
def email_list_invalidos(request):
    return request.param


@pytest.fixture
def fake_user(client):
    email = 'admin@admin.com'
    password = DJANGO_ADMIN_PASSWORD
    user = models.Usuario.objects.create_user(
        email=email,
        password=password,
        nome='admin',
        cpf='0',
        registro_funcional='1234',
    )
    return user, password


@pytest.fixture
def usuario_autenticado(client):
    email = 'admin@admin.com'
    password = DJANGO_ADMIN_PASSWORD
    client.login(username=email, password=password)
    return client


@pytest.fixture
def authenticated_client(client, fake_user):
    user, password = fake_user
    client.login(username=user.email, password=password)
    return client
