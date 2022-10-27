import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from .dados_comuns import constants
from .dados_comuns.models import TemplateMensagem

f = Faker(locale='pt-Br')


@pytest.fixture
def client_autenticado(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    django_user_model.objects.create_user(username=email, password=password, email=email,
                                          registro_funcional='8888888')
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_admin_django(client, django_user_model):
    email = 'admDoDjango@xxx.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    django_user_model.objects.create_user(username=email, password=password, email=email,
                                          registro_funcional='8888888',
                                          is_staff=True, )
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_vinculo_escola(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    lote = mommy.make('Lote', nome='lote', iniciais='lt')
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad')
    cardapio1 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 15))
    tipo_unidade_escolar = mommy.make('escola.TipoUnidadeEscolar',
                                      iniciais=f.name()[:10],
                                      cardapios=[cardapio1, cardapio2],
                                      uuid='56725de5-89d3-4edf-8633-3e0b5c99e9d4')
    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF',
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd', diretoria_regional=diretoria_regional,
                        codigo_eol='256341', tipo_unidade=tipo_unidade_escolar, lote=lote)
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_diretoria_regional(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_cogestor = mommy.make('Perfil',
                                 nome=constants.COGESTOR,
                                 ativo=True)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=diretoria_regional,
               perfil=perfil_cogestor,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_codae_gestao_alimentacao(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_gestao_alimentacao = mommy.make('Perfil',
                                                 nome=constants.ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                 ativo=True)
    codae = mommy.make('Codae')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=codae,
               perfil=perfil_admin_gestao_alimentacao,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_dilog(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_dilog = mommy.make('Perfil',
                                    nome=constants.COORDENADOR_LOGISTICA,
                                    ativo=True)
    codae = mommy.make('Codae')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=codae,
               perfil=perfil_admin_dilog,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_distribuidor(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_distribuidor = mommy.make('Perfil',
                                           nome=constants.ADMINISTRADOR_DISTRIBUIDORA,
                                           ativo=True)
    distribuidor = mommy.make('Terceirizada')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=distribuidor,
               perfil=perfil_admin_distribuidor,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_escola_abastecimento(client, django_user_model, escola):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_escola_abastecimento = mommy.make('Perfil',
                                                   nome=constants.ADMINISTRADOR_ESCOLA_ABASTECIMENTO,
                                                   ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_admin_escola_abastecimento,
               data_inicial=hoje, ativo=True)
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(username=email, password=password)
    return client
