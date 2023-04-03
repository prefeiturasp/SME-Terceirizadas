import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from .dados_comuns import constants
from .dados_comuns.models import TemplateMensagem
from .inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua

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
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR_UE', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad')
    cardapio1 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 15))
    tipo_unidade_escolar = mommy.make('escola.TipoUnidadeEscolar',
                                      iniciais=f.name()[:10],
                                      cardapios=[cardapio1, cardapio2],
                                      uuid='56725de5-89d3-4edf-8633-3e0b5c99e9d4')
    tipo_gestao = mommy.make('TipoGestao', nome='TERC TOTAL')
    escola = mommy.make('Escola', nome='EMEI NOE AZEVEDO, PROF',
                        uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd', diretoria_regional=diretoria_regional,
                        tipo_gestao=tipo_gestao, codigo_eol='256341', tipo_unidade=tipo_unidade_escolar, lote=lote)
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
                                 nome=constants.COGESTOR_DRE,
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
def client_autenticado_codae_dilog(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_dilog = mommy.make('Perfil',
                                    nome=constants.COORDENADOR_CODAE_DILOG_LOGISTICA,
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
def client_autenticado_qualidade(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_qualidade = mommy.make('Perfil',
                                        nome=constants.DILOG_QUALIDADE,
                                        ativo=True)
    codae = mommy.make('Codae')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=codae,
               perfil=perfil_admin_qualidade,
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
                                           nome=constants.ADMINISTRADOR_EMPRESA,
                                           ativo=True)
    distribuidor = mommy.make('Terceirizada', tipo_servico='DISTRIBUIDOR_ARMAZEM')
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
def client_autenticado_fornecedor(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_fornecedor = mommy.make('Perfil',
                                         nome=constants.ADMINISTRADOR_EMPRESA,
                                         ativo=True)
    fornecedor = mommy.make('Terceirizada', tipo_servico='FORNECEDOR')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=fornecedor,
               perfil=perfil_admin_fornecedor,
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
                                                   nome=constants.ADMINISTRADOR_UE,
                                                   ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_admin_escola_abastecimento,
               data_inicial=hoje, ativo=True)
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_dilog_cronograma(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email,
                                                 password=password, email=email, registro_funcional='8888888')
    perfil_admin_dilog = mommy.make('Perfil',
                                    nome=constants.DILOG_CRONOGRAMA,
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
def client_autenticado_dinutre_diretoria(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_dilog = mommy.make('Perfil',
                                    nome=constants.DINUTRE_DIRETORIA,
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
def client_autenticado_dilog_diretoria(client, django_user_model):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_dilog_diretoria = mommy.make('Perfil',
                                        nome=constants.DILOG_DIRETORIA,
                                        ativo=True)
    codae = mommy.make('Codae')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=codae,
               perfil=perfil_dilog_diretoria,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def diretoria_regional_ip():
    return mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA', iniciais='IP',
                      uuid='7da9acec-48e1-430c-8a5c-1f1efc666fad', codigo_eol=987656)


@pytest.fixture
def escola_um(diretoria_regional_ip):
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    return mommy.make('Escola', lote=lote, diretoria_regional=diretoria_regional_ip,
                      uuid='a7b9cf39-ab0a-4c6f-8e42-230243f9763f')


@pytest.fixture
def inclusoes_continuas(terceirizada, escola_um):
    inclusao = mommy.make('InclusaoAlimentacaoContinua',
                          escola=escola_um,
                          status=InclusaoAlimentacaoContinua.workflow_class.CODAE_AUTORIZADO
                          )
    return inclusao


@pytest.fixture
def inclusoes_normais(terceirizada, escola_um):
    return mommy.make('GrupoInclusaoAlimentacaoNormal',
                      escola=escola_um,
                      status=GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO
                      )


@pytest.fixture
def alteracoes_cardapio(terceirizada, escola_um):
    return mommy.make('AlteracaoCardapio')
