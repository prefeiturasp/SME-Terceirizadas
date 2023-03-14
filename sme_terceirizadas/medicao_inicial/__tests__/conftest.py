import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy


@pytest.fixture
def tipo_unidade_escolar():
    return mommy.make('TipoUnidadeEscolar', iniciais='EMEF')


@pytest.fixture
def dia_sobremesa_doce(tipo_unidade_escolar):
    return mommy.make('DiaSobremesaDoce', data=datetime.date(2022, 8, 8), tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def client_autenticado_coordenador_codae(client, django_user_model):
    email, password, rf, cpf = ('cogestor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052')
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)

    codae = mommy.make('Codae', nome='CODAE', uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_coordenador = mommy.make('Perfil', nome='COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA', ativo=True,
                                    uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    mommy.make('Lote', uuid='143c2550-8bf0-46b4-b001-27965cfcd107')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_coordenador,
               data_inicial=hoje, ativo=True)
    emef = mommy.make('TipoUnidadeEscolar', iniciais='EMEF', uuid='1cc3253b-e297-42b3-8e57-ebfd115a1aba')
    mommy.make('Escola', tipo_unidade=emef, uuid='95ad02fb-d746-4e0c-95f4-0181a99bc192')
    mommy.make('TipoUnidadeEscolar', iniciais='CEU GESTAO', uuid='40ee89a7-dc70-4abb-ae21-369c67f2b9e3')
    mommy.make('TipoUnidadeEscolar', iniciais='CIEJA', uuid='ac4858ff-1c11-41f3-b539-7a02696d6d1b')
    return client


@pytest.fixture
def escola():
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='9640fef4-a068-474e-8979-2e1b2654357a')
    return mommy.make('Escola', nome='EMEF TESTE', lote=lote, diretoria_regional=diretoria_regional)


@pytest.fixture
def solicitacao_medicao_inicial(escola, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial', uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes=12, ano=2022, escola=escola, tipo_contagem_alimentacoes=tipo_contagem)
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_manha)
    mommy.make('ValorMedicao', dia='01', nome_campo='lanche', medicao=medicao, categoria_medicao=categoria_medicao,
               valor='10')
    return solicitacao_medicao


@pytest.fixture
def solicitacao_medicao_inicial_varios_valores(escola, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    periodo_tarde = mommy.make('PeriodoEscolar', nome='TARDE')
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', mes=12, ano=2022, escola=escola,
                                     tipo_contagem_alimentacoes=tipo_contagem)
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_manha)
    grupo = mommy.make('GrupoMedicao', nome='Programas Projetos')
    medicao_programas_projetos = mommy.make(
        'Medicao', solicitacao_medicao_inicial=solicitacao_medicao, periodo_escolar=periodo_tarde, grupo=grupo)
    categoria_dieta_a = mommy.make('CategoriaMedicao', nome='DIETA ESPECIAL - TIPO A ENTERAL')
    categoria_dieta_b = mommy.make('CategoriaMedicao', nome='DIETA ESPECIAL - TIPO B')
    for dia in ['01', '02', '03', '04', '05']:
        for campo in ['lanche', 'refeicao', 'lanche_emergencial', 'sobremesa']:
            for categoria in [categoria_medicao, categoria_dieta_a, categoria_dieta_b]:
                for medicao_ in [medicao, medicao_programas_projetos]:
                    mommy.make('ValorMedicao', dia=dia, nome_campo=campo, medicao=medicao_,
                               categoria_medicao=categoria,
                               valor='10')
    return solicitacao_medicao


@pytest.fixture
def solicitacao_medicao_inicial_com_grupo(escola):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    grupo = mommy.make('GrupoMedicao', nome='Programas e Projetos')
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial', uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes=12, ano=2022, escola=escola, tipo_contagem_alimentacoes=tipo_contagem)
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_manha, grupo=grupo)
    mommy.make('ValorMedicao', medicao=medicao)
    return solicitacao_medicao


@pytest.fixture
def solicitacoes_medicao_inicial(escola):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    escola_2 = mommy.make('Escola')
    s1 = mommy.make('SolicitacaoMedicaoInicial', mes=12, ano=2022, escola=escola,
                    tipo_contagem_alimentacoes=tipo_contagem, status='MEDICAO_ENVIADA_PELA_UE')
    s2 = mommy.make('SolicitacaoMedicaoInicial', mes=1, ano=2023, escola=escola,
                    tipo_contagem_alimentacoes=tipo_contagem, status='MEDICAO_ENVIADA_PELA_UE')
    s3 = mommy.make('SolicitacaoMedicaoInicial', mes=2, ano=2023, escola=escola,
                    tipo_contagem_alimentacoes=tipo_contagem, status='MEDICAO_CORRECAO_SOLICITADA')
    s4 = mommy.make('SolicitacaoMedicaoInicial', mes=2, ano=2023, escola=escola_2,
                    tipo_contagem_alimentacoes=tipo_contagem, status='MEDICAO_CORRECAO_SOLICITADA')
    s5 = mommy.make('SolicitacaoMedicaoInicial', mes=3, ano=2023, escola=escola,
                    tipo_contagem_alimentacoes=tipo_contagem, status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE')
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s1.uuid,
               status_evento=55,  # MEDICAO_ENVIADA_PELA_UE
               solicitacao_tipo=16)  # MEDICAO_INICIAL
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s2.uuid,
               status_evento=55,  # MEDICAO_ENVIADA_PELA_UE
               solicitacao_tipo=16)  # MEDICAO_INICIAL
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s3.uuid,
               status_evento=64,  # MEDICAO_CORRECAO_SOLICITADA
               solicitacao_tipo=16)  # MEDICAO_INICIAL
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s4.uuid,
               status_evento=64,  # MEDICAO_CORRECAO_SOLICITADA
               solicitacao_tipo=16)  # MEDICAO_INICIAL
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s5.uuid,
               status_evento=54,  # MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE
               solicitacao_tipo=16)  # MEDICAO_INICIAL


@pytest.fixture
def solicitacao_medicao_inicial_sem_arquivo(escola):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas COloridas')
    return mommy.make('SolicitacaoMedicaoInicial', uuid='fb6d1870-a397-4e87-8218-13d316a0ffea',
                      mes=6, ano=2022, escola=escola, tipo_contagem_alimentacoes=tipo_contagem)


@pytest.fixture
def anexo_ocorrencia_medicao_inicial(solicitacao_medicao_inicial):
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    return mommy.make('AnexoOcorrenciaMedicaoInicial', uuid='1ace193a-6c2c-4686-b9ed-60a922ad0e1a',
                      nome=nome, arquivo=arquivo, solicitacao_medicao_inicial=solicitacao_medicao_inicial)


@pytest.fixture
def responsavel(solicitacao_medicao_inicial):
    nome = 'tester'
    rf = '1234567'
    return mommy.make('medicao_inicial.Responsavel', nome=nome, rf=rf,
                      solicitacao_medicao_inicial=solicitacao_medicao_inicial)


@pytest.fixture
def tipo_contagem_alimentacao():
    return mommy.make('TipoContagemAlimentacao', nome='Fichas')


@pytest.fixture
def periodo_escolar():
    return mommy.make('PeriodoEscolar', nome='INTEGRAL')


@pytest.fixture
def medicao(solicitacao_medicao_inicial, periodo_escolar):
    return mommy.make('Medicao', periodo_escolar=periodo_escolar, uuid='5a3a3941-1b91-4b9f-b410-c3547e224eb5',
                      solicitacao_medicao_inicial=solicitacao_medicao_inicial)


@pytest.fixture
def categoria_medicao():
    return mommy.make('CategoriaMedicao', nome='ALIMENTAÇÃO')


@pytest.fixture
def valor_medicao(medicao, categoria_medicao):
    valor = 13
    nome_campo = 'observacoes'
    tipo_alimentacao = mommy.make('TipoAlimentacao', nome='Lanche', uuid='b58b7946-67c4-416c-82cf-f26a470fb93e')
    return mommy.make('ValorMedicao', valor=valor, nome_campo=nome_campo, medicao=medicao,
                      uuid='fc2fbc0a-8dda-4c8e-b5cf-c40ecff52a5c', dia=13,
                      categoria_medicao=categoria_medicao, tipo_alimentacao=tipo_alimentacao)


@pytest.fixture
def client_autenticado_diretoria_regional(client, django_user_model, escola):
    email = 'test@test.com'
    password = 'admin@123'
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional='8888888')
    perfil_cogestor = mommy.make('Perfil',
                                 nome='COGESTOR',
                                 ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=escola.diretoria_regional,
               perfil=perfil_cogestor,
               data_inicial=hoje,
               ativo=True)
    client.login(email=email, password=password)
    return client


@pytest.fixture
def client_autenticado_da_escola(client, django_user_model, escola):
    email = 'user@escola.com'
    password = 'admin@123'
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
def client_autenticado_adm_da_escola(client, django_user_model, escola):
    email = 'user@escola_adm.com'
    password = 'admin@1234'
    perfil_diretor = mommy.make('Perfil', nome='ADMINISTRADOR_UE', ativo=True)
    usuario = django_user_model.objects.create_user(password=password, email=email,
                                                    registro_funcional='1234567',
                                                    )
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    client.login(email=email, password=password)
    return client
