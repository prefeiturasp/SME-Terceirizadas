import datetime

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from model_mommy import mommy

from ...dados_comuns import constants
from ...dados_comuns.constants import DJANGO_ADMIN_PASSWORD
from ...dados_comuns.fluxo_status import HomologacaoProdutoWorkflow, ReclamacaoProdutoWorkflow
from ...dados_comuns.models import TemplateMensagem
from ..models import ProdutoEdital

fake = Faker('pt-Br')
fake.seed(420)


@pytest.fixture
def escola():
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='9640fef4-a068-474e-8979-2e1b2654357a')
    return mommy.make('Escola', lote=lote, diretoria_regional=diretoria_regional)


@pytest.fixture
def codae():
    return mommy.make('Codae')


@pytest.fixture
def template_homologacao_produto():
    return mommy.make(TemplateMensagem, assunto='TESTE',
                      tipo=TemplateMensagem.HOMOLOGACAO_PRODUTO,
                      template_html='@id @criado_em @status @link')


@pytest.fixture
def client_autenticado_vinculo_codae_produto(client, django_user_model, escola, codae, template_homologacao_produto):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_gestao_produto = mommy.make('Perfil', nome=constants.ADMINISTRADOR_GESTAO_PRODUTO,
                                             ativo=True,
                                             uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_admin_gestao_produto,
               data_inicial=hoje, ativo=True)
    client.login(email=email, password=password)
    return client


@pytest.fixture
def client_autenticado_vinculo_terceirizada(client, django_user_model, escola, template_homologacao_produto):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    tecerizada = escola.lote.terceirizada
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_admin_terceirizada = mommy.make('Perfil', nome=constants.ADMINISTRADOR_TERCEIRIZADA,
                                           ativo=True,
                                           uuid='41c20c8b-7e57-41ed-9433-ccb95e8afaf0')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=tecerizada, perfil=perfil_admin_terceirizada,
               data_inicial=hoje, ativo=True)
    client.login(email=email, password=password)
    return client


@pytest.fixture
def user(django_user_model):
    email = 'test@test1.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    return django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888881')


@pytest.fixture
def client_autenticado_vinculo_terceirizada_homologacao(client, django_user_model, escola):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    tecerizada = escola.lote.terceirizada
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_diretor = mommy.make('Perfil', nome=constants.ADMINISTRADOR_TERCEIRIZADA,
                                ativo=True,
                                uuid='41c20c8b-7e57-41ed-9433-ccb95e8afaf0')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=tecerizada, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    produto = mommy.make('Produto', criado_por=user)
    homologacao_produto = mommy.make('HomologacaoProduto',
                                     produto=produto,
                                     rastro_terceirizada=escola.lote.terceirizada,
                                     criado_por=user,
                                     criado_em=datetime.datetime.utcnow(),
                                     uuid='774ad907-d871-4bfd-b1aa-d4e0ecb6c01f')
    homologacao_produto.status = HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_SENSORIAL
    homologacao_produto.save()
    client.login(email=email, password=password)
    return client, homologacao_produto


@pytest.fixture
def protocolo1():
    return mommy.make('ProtocoloDeDietaEspecial', nome='Protocolo1')


@pytest.fixture
def protocolo2():
    return mommy.make('ProtocoloDeDietaEspecial', nome='Protocolo2')


@pytest.fixture
def protocolo3():
    return mommy.make('ProtocoloDeDietaEspecial', nome='Protocolo3')


@pytest.fixture
def marca1():
    return mommy.make('Marca', nome='Marca1')


@pytest.fixture
def marca2():
    return mommy.make('Marca', nome='Marca2')


@pytest.fixture
def fabricante():
    return mommy.make('Fabricante', nome='Fabricante1')


@pytest.fixture
def unidade_medida():
    return mommy.make('UnidadeMedida', nome='Litros')


@pytest.fixture
def embalagem_produto():
    return mommy.make('EmbalagemProduto', nome='Bag')


@pytest.fixture
def terceirizada():
    return mommy.make('Terceirizada',
                      contatos=[mommy.make('dados_comuns.Contato')],
                      make_m2m=True,
                      nome_fantasia='Alimentos SA'
                      )


@pytest.fixture
def edital():
    return mommy.make('Edital',
                      uuid='617a8139-02a9-4801-a197-622aa20795b9',
                      numero='Edital de Pregão nº 56/SME/2016',
                      tipo_contratacao='Teste',
                      processo='Teste',
                      objeto='Teste')


@pytest.fixture
def produto(user, protocolo1, protocolo2, marca1, fabricante):
    return mommy.make('Produto',
                      uuid='a37bcf3f-a288-44ae-87ae-dbec181a34d4',
                      criado_por=user,
                      eh_para_alunos_com_dieta=True,
                      componentes='Componente1, Componente2',
                      tem_aditivos_alergenicos=False,
                      tipo='Tipo1',
                      embalagem='Embalagem X',
                      prazo_validade='Alguns dias',
                      info_armazenamento='Guardem bem',
                      outras_informacoes='Produto do bom',
                      numero_registro='123123123',
                      porcao='5 cuias',
                      unidade_caseira='Unidade3',
                      nome='Produto1',
                      fabricante=fabricante,
                      marca=marca1,
                      protocolos=[
                          protocolo1,
                          protocolo2,
                      ])


@pytest.fixture
def homologacoes_produto(produto, terceirizada):
    hom = mommy.make('HomologacaoProduto',
                     produto=produto,
                     rastro_terceirizada=terceirizada,
                     status=HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO)
    mommy.make('LogSolicitacoesUsuario', uuid_original=hom.uuid)
    return hom


@pytest.fixture
def vinculo_produto_edital(produto, edital):
    produto_edital = mommy.make('ProdutoEdital',
                                produto=produto,
                                edital=edital,
                                outras_informacoes='Teste 1',
                                ativo=True,
                                tipo_produto=ProdutoEdital.TIPO_PRODUTO['DIETA_ESPECIAL'])
    return produto_edital


@pytest.fixture
def client_autenticado_da_terceirizada(client, django_user_model, terceirizada):
    email = 'foo@codae.com'
    password = DJANGO_ADMIN_PASSWORD
    perfil_adm_terc = mommy.make('Perfil', nome='TERCEIRIZADA', ativo=True)
    usuario = django_user_model.objects.create_user(password=password, email=email,
                                                    registro_funcional='123456')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=terceirizada, perfil=perfil_adm_terc,
               data_inicial=hoje, ativo=True)
    client.login(email=email, password=password)
    return client


@pytest.fixture
def client_autenticado_da_escola(client, django_user_model, escola):
    email = 'user@escola.com'
    password = DJANGO_ADMIN_PASSWORD
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True)
    usuario = django_user_model.objects.create_user(password=password, email=email,
                                                    registro_funcional='123456',
                                                    )
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    client.login(email=email, password=password)
    return client


@pytest.fixture
def info_nutricional1():
    return mommy.make('InformacaoNutricional', nome='CALORIAS')


@pytest.fixture
def info_nutricional2():
    return mommy.make('InformacaoNutricional', nome='LACTOSE')


@pytest.fixture
def info_nutricional3():
    return mommy.make('InformacaoNutricional', nome='COLESTEROL')


@pytest.fixture
def info_nutricional_produto1(produto, info_nutricional1):
    return mommy.make(
        'InformacoesNutricionaisDoProduto',
        produto=produto,
        informacao_nutricional=info_nutricional1,
        quantidade_porcao='1',
        valor_diario='2')


@pytest.fixture
def info_nutricional_produto2(produto, info_nutricional2):
    return mommy.make(
        'InformacoesNutricionaisDoProduto',
        produto=produto,
        informacao_nutricional=info_nutricional2,
        quantidade_porcao='3',
        valor_diario='4')


@pytest.fixture
def info_nutricional_produto3(produto, info_nutricional3):
    return mommy.make(
        'InformacoesNutricionaisDoProduto',
        produto=produto,
        informacao_nutricional=info_nutricional3,
        quantidade_porcao='5',
        valor_diario='6')


@pytest.fixture
def especificacao_produto1(produto, unidade_medida, embalagem_produto):
    return mommy.make('EspecificacaoProduto',
                      volume=1.5,
                      produto=produto,
                      unidade_de_medida=unidade_medida,
                      embalagem_produto=embalagem_produto)


@pytest.fixture
def produto_edital(user):
    return mommy.make('NomeDeProdutoEdital',
                      nome='PRODUTO TESTE',
                      ativo=True,
                      criado_por=user)


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(f'planilha-teste.pdf', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding='utf-8'))


@pytest.fixture
def imagem_produto1(produto, arquivo):
    return mommy.make('ImagemDoProduto', produto=produto, nome='Imagem1', arquivo=arquivo)


@pytest.fixture
def imagem_produto2(produto, arquivo):
    return mommy.make('ImagemDoProduto', produto=produto, nome='Imagem2', arquivo=arquivo)


@pytest.fixture
def client_autenticado_vinculo_escola_ue(client, django_user_model, escola):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')

    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(email=email, password=password)
    return client


@pytest.fixture
def client_autenticado_vinculo_escola_nutrisupervisor(
        client,
        django_user_model,
        escola):

    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')

    perfil_nutri = mommy.make('Perfil', nome='COORDENADOR_SUPERVISAO_NUTRICAO',
                              ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_nutri,
               data_inicial=hoje, ativo=True)
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(email=email, password=password)
    return client


@pytest.fixture
def client_autenticado_vinculo_codae_nutrisupervisor(
        client,
        django_user_model,
        codae):

    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(password=password, email=email,
                                                 registro_funcional='8888888')

    perfil_nutri = mommy.make('Perfil', nome='COORDENADOR_SUPERVISAO_NUTRICAO',
                              ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_nutri,
               data_inicial=hoje, ativo=True)
    assert user.tipo_usuario == constants.TIPO_USUARIO_NUTRISUPERVISOR
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.DIETA_ESPECIAL,
               template_html='@id @criado_em @status @link')
    client.login(email=email, password=password)
    return client


@pytest.fixture
def homologacao_produto(escola, template_homologacao_produto, user, produto):
    perfil_admin_terceirizada = mommy.make('Perfil', nome=constants.ADMINISTRADOR_TERCEIRIZADA,
                                           ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola.lote.terceirizada, perfil=perfil_admin_terceirizada,
               data_inicial=hoje, ativo=True)
    homologacao_produto = mommy.make('HomologacaoProduto',
                                     produto=produto,
                                     rastro_terceirizada=escola.lote.terceirizada,
                                     criado_por=user,
                                     criado_em=datetime.datetime.utcnow())
    return homologacao_produto


@pytest.fixture
def homologacao_produto_pendente_homologacao(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def homologacao_produto_homologado(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def homologacao_produto_homologado_com_log(homologacao_produto, user):
    homologacao_produto.inicia_fluxo(user=user)
    return homologacao_produto


@pytest.fixture
def homologacao_produto_escola_ou_nutri_reclamou(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def reclamacao(homologacao_produto_escola_ou_nutri_reclamou, escola, user):
    reclamacao = mommy.make('ReclamacaoDeProduto',
                            homologacao_produto=homologacao_produto_escola_ou_nutri_reclamou,
                            escola=escola,
                            reclamante_registro_funcional='23456789',
                            reclamante_cargo='Cargo',
                            reclamante_nome='Anderson',
                            criado_por=user,
                            criado_em=datetime.datetime.utcnow())
    return reclamacao


@pytest.fixture
def homologacao_produto_gpcodae_questionou_escola(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_UE
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def homologacao_produto_gpcodae_questionou_nutrisupervisor(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.CODAE_QUESTIONOU_NUTRISUPERVISOR
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def homologacao_produto_rascunho(homologacao_produto):
    homologacao_produto.status = HomologacaoProdutoWorkflow.RASCUNHO
    homologacao_produto.save()
    return homologacao_produto


@pytest.fixture
def reclamacao_ue(homologacao_produto_gpcodae_questionou_escola, escola, user):
    reclamacao = mommy.make('ReclamacaoDeProduto',
                            homologacao_produto=homologacao_produto_gpcodae_questionou_escola,
                            escola=escola,
                            reclamante_registro_funcional='23456788',
                            reclamante_cargo='Cargo',
                            reclamante_nome='Arthur',
                            criado_por=user,
                            criado_em=datetime.datetime.utcnow(),
                            status=ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_UE)
    return reclamacao


@pytest.fixture
def reclamacao_nutrisupervisor(homologacao_produto_gpcodae_questionou_nutrisupervisor, escola, user):
    reclamacao = mommy.make('ReclamacaoDeProduto',
                            homologacao_produto=homologacao_produto_gpcodae_questionou_nutrisupervisor,
                            escola=escola,
                            reclamante_registro_funcional='8888888',
                            reclamante_cargo='Cargo',
                            reclamante_nome='Arthur',
                            criado_por=user,
                            criado_em=datetime.datetime.utcnow(),
                            status=ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_NUTRISUPERVISOR)
    return reclamacao


@pytest.fixture
def item_cadastrado_1(marca1):
    return mommy.make('ItemCadastro',
                      tipo='MARCA',
                      content_type=ContentType.objects.get(model='marca'),
                      content_object=marca1)


@pytest.fixture
def item_cadastrado_2(fabricante):
    return mommy.make('ItemCadastro',
                      tipo='FABRICANTE',
                      content_type=ContentType.objects.get(model='fabricante'),
                      content_object=fabricante)


@pytest.fixture
def item_cadastrado_3(unidade_medida):
    return mommy.make('ItemCadastro',
                      tipo='UNIDADE_MEDIDA',
                      content_type=ContentType.objects.get(model='unidademedida'),
                      content_object=unidade_medida)


@pytest.fixture
def item_cadastrado_4(embalagem_produto):
    return mommy.make('ItemCadastro',
                      tipo='EMBALAGEM',
                      content_type=ContentType.objects.get(model='embalagemproduto'),
                      content_object=embalagem_produto)


@pytest.fixture
def usuario():
    return mommy.make('perfil.Usuario')
