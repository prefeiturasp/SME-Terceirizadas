import datetime
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy

from sme_terceirizadas.dados_comuns.behaviors import TempoPasseio


@pytest.fixture
def kit_lanche_1():
    return mommy.make('KitLanche', nome='KIT 1')


@pytest.fixture
def kit_lanche_2():
    return mommy.make('KitLanche', nome='KIT 2')


@pytest.fixture
def grupo_programas_e_projetos():
    return mommy.make('GrupoMedicao', nome='Programas e Projetos')


@pytest.fixture
def grupo_etec():
    return mommy.make('GrupoMedicao', nome='ETEC')


@pytest.fixture
def grupo_solicitacoes_alimentacao():
    return mommy.make('GrupoMedicao', nome='Solicitações de Alimentação')


@pytest.fixture
def motivo_inclusao_continua_programas_projetos():
    return mommy.make('MotivoInclusaoContinua', nome='Programas/Projetos Contínuos')


@pytest.fixture
def motivo_inclusao_continua_etec():
    return mommy.make('MotivoInclusaoContinua', nome='ETEC')


@pytest.fixture
def tipo_alimentacao_refeicao():
    return mommy.make('TipoAlimentacao', nome='Refeição')


@pytest.fixture
def tipo_alimentacao_lanche():
    return mommy.make('TipoAlimentacao', nome='Lanche')


@pytest.fixture
def classificacao_dieta_tipo_a():
    return mommy.make('ClassificacaoDieta', nome='Tipo A')


@pytest.fixture
def classificacao_dieta_tipo_a_enteral():
    return mommy.make('ClassificacaoDieta', nome='Tipo A ENTERAL')


@pytest.fixture
def tipo_unidade_escolar():
    return mommy.make('TipoUnidadeEscolar', iniciais='EMEF')


@pytest.fixture
def dia_sobremesa_doce(tipo_unidade_escolar):
    return mommy.make('DiaSobremesaDoce', data=datetime.date(2022, 8, 8), tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def client_autenticado_coordenador_codae(client, django_user_model):
    email, password, rf, cpf = ('cogestor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052')
    user = django_user_model.objects.create_user(username=email, password=password, email=email, registro_funcional=rf,
                                                 cpf=cpf)
    client.login(username=email, password=password)

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
def escola(tipo_unidade_escolar):
    terceirizada = mommy.make('Terceirizada')
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL IPIRANGA',
                                    uuid='9640fef4-a068-474e-8979-2e1b2654357a')
    lote = mommy.make('Lote', terceirizada=terceirizada, diretoria_regional=diretoria_regional)
    tipo_gestao = mommy.make('TipoGestao', nome='TERC TOTAL')
    return mommy.make('Escola', nome='EMEF TESTE', lote=lote, diretoria_regional=diretoria_regional,
                      tipo_gestao=tipo_gestao, tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def escola_emei():
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL TESTE')
    tipo_gestao = mommy.make('TipoGestao', nome='TERC TOTAL')
    tipo_unidade_escolar = mommy.make('TipoUnidadeEscolar', iniciais='EMEI')
    return mommy.make('Escola', nome='EMEI TESTE', lote=lote, diretoria_regional=diretoria_regional,
                      tipo_gestao=tipo_gestao, tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def escola_cei():
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL TESTE')
    tipo_gestao = mommy.make('TipoGestao', nome='TERC TOTAL')
    tipo_unidade_escolar = mommy.make('TipoUnidadeEscolar', iniciais='CEI DIRET')
    return mommy.make('Escola', nome='CEI DIRET TESTE', lote=lote, diretoria_regional=diretoria_regional,
                      tipo_gestao=tipo_gestao, tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def escola_cemei():
    terceirizada = mommy.make('Terceirizada')
    lote = mommy.make('Lote', terceirizada=terceirizada)
    diretoria_regional = mommy.make('DiretoriaRegional', nome='DIRETORIA REGIONAL TESTE')
    tipo_gestao = mommy.make('TipoGestao', nome='TERC TOTAL')
    tipo_unidade_escolar = mommy.make('TipoUnidadeEscolar', iniciais='CEMEI')
    return mommy.make('Escola', nome='CEMEI TESTE', lote=lote, diretoria_regional=diretoria_regional,
                      tipo_gestao=tipo_gestao, tipo_unidade=tipo_unidade_escolar)


@pytest.fixture
def aluno():
    return mommy.make('Aluno', nome='Roberto Alves da Silva', codigo_eol='123456', data_nascimento='2000-01-01',
                      uuid='2d20157a-4e52-4d25-a4c7-9c0e6b67ee18')


@pytest.fixture
def solicitacao_medicao_inicial_cemei(escola_cemei, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_integral = mommy.make('PeriodoEscolar', nome='INTEGRAL')
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', mes=4, ano=2023, escola=escola_cemei)
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao, periodo_escolar=periodo_integral)
    mommy.make('FaixaEtaria', inicio=1, fim=10, uuid='0c914b27-c7cd-4682-a439-a4874745b005')
    return solicitacao_medicao


@pytest.fixture
def solicitacao_medicao_inicial(escola, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    historico = {
        'usuario': {'uuid': 'a7f20675-50e1-46d2-a207-28543b93e19d', 'nome': 'usuario teste',
                    'username': '12312312344', 'email': 'email@teste.com'},
        'criado_em': datetime.date.today().strftime('%Y-%m-%d %H:%M:%S'),
        'acao': 'MEDICAO_CORRECAO_SOLICITADA',
        'alteracoes': [
            {
                'periodo_escolar': periodo_manha.nome,
                'tabelas_lancamentos': [
                    {
                        'categoria_medicao': 'ALIMENTAÇÃO',
                        'semanas': [
                            {'semana': '1', 'dias': ['01']}
                        ]
                    }
                ]
            },
        ]
    }
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial', uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes=12, ano=2022, escola=escola, historico=json.dumps([historico]))
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_manha)
    mommy.make('ValorMedicao', dia='01', semana='1', nome_campo='lanche', medicao=medicao,
               categoria_medicao=categoria_medicao, valor='10')
    return solicitacao_medicao


@pytest.fixture
def solicitacao_medicao_inicial_medicao_enviada_pela_ue(solicitacao_medicao_inicial):
    for medicao in solicitacao_medicao_inicial.medicoes.all():
        medicao.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_DRE
        medicao.save()
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_ENVIADA_PELA_UE
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_correcao_solicitada(solicitacao_medicao_inicial):
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_correcao_solicitada_codae(solicitacao_medicao_inicial):
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA_CODAE
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_aprovada_pela_dre_ok(solicitacao_medicao_inicial):
    for medicao in solicitacao_medicao_inicial.medicoes.all():
        medicao.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_CODAE
        medicao.save()
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_DRE
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_aprovada_pela_dre_nok(solicitacao_medicao_inicial):
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_DRE
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_enviada_pela_ue_nok(solicitacao_medicao_inicial):
    for medicao in solicitacao_medicao_inicial.medicoes.all():
        medicao.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_CODAE
        medicao.save()
    solicitacao_medicao_inicial.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_ENVIADA_PELA_UE
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_medicao_enviada_pela_ue_nok__2(solicitacao_medicao_inicial):
    for medicao in solicitacao_medicao_inicial.medicoes.all():
        medicao.status = solicitacao_medicao_inicial.workflow_class.MEDICAO_APROVADA_PELA_DRE
        medicao.save()
    status = solicitacao_medicao_inicial.workflow_class.MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE
    solicitacao_medicao_inicial.status = status
    solicitacao_medicao_inicial.save()
    return solicitacao_medicao_inicial


@pytest.fixture
def solicitacao_medicao_inicial_varios_valores(escola, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    periodo_tarde = mommy.make('PeriodoEscolar', nome='TARDE')
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', mes=12, ano=2022, escola=escola)
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_manha)
    medicao_programas_projetos = mommy.make(
        'Medicao', solicitacao_medicao_inicial=solicitacao_medicao, periodo_escolar=periodo_tarde)
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
def solicitacao_medicao_inicial_com_valores_repeticao(escola, categoria_medicao):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    periodo_tarde = mommy.make('PeriodoEscolar', nome='TARDE')
    periodo_integral = mommy.make('PeriodoEscolar', nome='INTEGRAL')
    periodo_noite = mommy.make('PeriodoEscolar', nome='NOITE')
    grupo_solicitacoes_alimentacao = mommy.make('GrupoMedicao', nome='Solicitações de Alimentação')
    grupo_programas_e_projetos = mommy.make('GrupoMedicao', nome='Programas e Projetos')
    grupo_etec = mommy.make('GrupoMedicao', nome='ETEC')
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', mes=4, ano=2023, escola=escola)
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    medicao_manha = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                               periodo_escolar=periodo_manha)
    medicao_tarde = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                               periodo_escolar=periodo_tarde)
    medicao_integral = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                                  periodo_escolar=periodo_integral)
    medicao_noite = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                               periodo_escolar=periodo_noite)
    medicao_solicitacoes_alimentacao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                                                  grupo=grupo_solicitacoes_alimentacao)
    medicao_programas_e_projetos = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                                              grupo=grupo_programas_e_projetos)
    medicao_etec = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                              grupo=grupo_etec)
    for dia in ['10', '11']:
        campos = [
            'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa',
            'repeticao_refeicao', 'kit_lanche', 'repeticao_sobremesa'
        ]
        for campo in campos:
            for medicao_ in [
                medicao_manha, medicao_tarde, medicao_integral,
                medicao_noite, medicao_solicitacoes_alimentacao,
                medicao_programas_e_projetos, medicao_etec
            ]:
                mommy.make('ValorMedicao', dia=dia, nome_campo=campo, medicao=medicao_,
                           categoria_medicao=categoria_medicao, valor='25')
    return solicitacao_medicao


@pytest.fixture
def medicao_solicitacoes_alimentacao(escola):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    categoria = mommy.make('CategoriaMedicao', nome='SOLICITAÇÕES DE ALIMENTAÇÃO')
    grupo = mommy.make('GrupoMedicao', nome='Solicitações de Alimentação')
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', mes=6, ano=2023, escola=escola)
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    medicao_solicitacoes_alimentacao = mommy.make(
        'Medicao', solicitacao_medicao_inicial=solicitacao_medicao, periodo_escolar=None, grupo=grupo)
    for dia in ['01', '02', '03', '04', '05']:
        for campo in ['lanche', 'refeicao', 'lanche_emergencial', 'sobremesa', 'kit_lanche']:
            mommy.make('ValorMedicao', dia=dia, nome_campo=campo, medicao=medicao_solicitacoes_alimentacao,
                       categoria_medicao=categoria, valor='10')
    return medicao_solicitacoes_alimentacao


@pytest.fixture
def periodo_escolar_manha():
    return mommy.make('PeriodoEscolar', nome='MANHA')


@pytest.fixture
def periodo_escolar_tarde():
    return mommy.make('PeriodoEscolar', nome='TARDE')


@pytest.fixture
def periodo_escolar_noite():
    return mommy.make('PeriodoEscolar', nome='NOITE')


@pytest.fixture
def categoria_alimentacoes():
    return mommy.make('Cate')


@pytest.fixture
def escola_com_logs_para_medicao(periodo_escolar_manha, periodo_escolar_tarde, periodo_escolar_noite, escola,
                                 classificacao_dieta_tipo_a, classificacao_dieta_tipo_a_enteral,
                                 tipo_alimentacao_refeicao, tipo_alimentacao_lanche, grupo_programas_e_projetos,
                                 motivo_inclusao_continua_programas_projetos, motivo_inclusao_continua_etec,
                                 kit_lanche_1, kit_lanche_2):
    inclusao_continua_programas_projetos = mommy.make(
        'InclusaoAlimentacaoContinua',
        escola=escola,
        rastro_escola=escola,
        data_inicial=datetime.date(2023, 9, 1),
        data_final=datetime.date(2023, 9, 30),
        motivo=motivo_inclusao_continua_programas_projetos,
        status='CODAE_AUTORIZADO'
    )

    inclusao_continua_etec = mommy.make(
        'InclusaoAlimentacaoContinua',
        escola=escola,
        rastro_escola=escola,
        data_inicial=datetime.date(2023, 8, 15),
        data_final=datetime.date(2023, 9, 15),
        motivo=motivo_inclusao_continua_etec,
        status='CODAE_AUTORIZADO'
    )

    solicitacao_kit_lanche = mommy.make(
        'SolicitacaoKitLanche',
        data=datetime.date(2023, 9, 12),
        tempo_passeio=TempoPasseio.OITO_OU_MAIS
    )
    solicitacao_kit_lanche.kits.add(kit_lanche_1)
    solicitacao_kit_lanche.kits.add(kit_lanche_2)
    solicitacao_kit_lanche.save()

    mommy.make(
        'SolicitacaoKitLancheAvulsa',
        solicitacao_kit_lanche=solicitacao_kit_lanche,
        status='CODAE_AUTORIZADO',
        escola=escola,
        quantidade_alunos=100
    )

    solicitacao_unificada = mommy.make(
        'SolicitacaoKitLancheUnificada',
        status='CODAE_AUTORIZADO',
        solicitacao_kit_lanche=solicitacao_kit_lanche,
        diretoria_regional=escola.lote.diretoria_regional,
        lista_kit_lanche_igual=False
    )
    eq = mommy.make(
        'EscolaQuantidade',
        solicitacao_unificada=solicitacao_unificada,
        escola=escola,
        quantidade_alunos=100)
    eq.kits.add(kit_lanche_1)
    eq.kits.add(kit_lanche_2)
    eq.save()

    for periodo in [periodo_escolar_manha, periodo_escolar_tarde, periodo_escolar_noite]:
        qp = mommy.make('QuantidadePorPeriodo',
                        inclusao_alimentacao_continua=inclusao_continua_programas_projetos,
                        periodo_escolar=periodo,
                        numero_alunos=10,
                        dias_semana=[0, 1, 2, 3, 4, 5, 6])
        qp.tipos_alimentacao.add(tipo_alimentacao_refeicao)
        qp.tipos_alimentacao.add(tipo_alimentacao_lanche)
        qp.save()

        qp = mommy.make('QuantidadePorPeriodo',
                        inclusao_alimentacao_continua=inclusao_continua_etec,
                        periodo_escolar=periodo,
                        numero_alunos=10,
                        dias_semana=[0, 1, 2, 3, 4, 5, 6])
        qp.tipos_alimentacao.add(tipo_alimentacao_refeicao)
        qp.tipos_alimentacao.add(tipo_alimentacao_lanche)
        qp.save()

        mommy.make('AlunosMatriculadosPeriodoEscola',
                   escola=escola,
                   periodo_escolar=periodo,
                   quantidade_alunos=100)

        vinculo_alimentacao = mommy.make(
            'VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar',
            tipo_unidade_escolar=escola.tipo_unidade,
            periodo_escolar=periodo
        )
        vinculo_alimentacao.tipos_alimentacao.add(tipo_alimentacao_refeicao)
        vinculo_alimentacao.tipos_alimentacao.add(tipo_alimentacao_lanche)
        vinculo_alimentacao.save()

        mommy.make('Aluno', escola=escola, periodo_escolar=periodo)

        for dia in range(1, 31):
            data = datetime.date(2023, 9, dia)
            log = mommy.make(
                'LogAlunosMatriculadosPeriodoEscola',
                escola=escola,
                periodo_escolar=periodo,
                quantidade_alunos=100)
            log.criado_em = data
            log.save()

            if periodo == periodo_escolar_manha:
                for classificacao in [classificacao_dieta_tipo_a, classificacao_dieta_tipo_a_enteral]:
                    mommy.make('LogQuantidadeDietasAutorizadas',
                               data=datetime.date(2023, 9, dia),
                               escola=escola,
                               periodo_escolar=periodo,
                               classificacao=classificacao,
                               quantidade=10)
    return escola


@pytest.fixture
def solicitacao_medicao_inicial_teste_salvar_logs(
        escola_com_logs_para_medicao, tipo_contagem_alimentacao, periodo_escolar_manha, periodo_escolar_tarde,
        periodo_escolar_noite, categoria_medicao, categoria_medicao_dieta_a, grupo_programas_e_projetos,
        categoria_medicao_dieta_a_enteral_aminoacidos, grupo_etec, grupo_solicitacoes_alimentacao,
        categoria_medicao_solicitacoes_alimentacao):
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial',
        uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes='09',
        ano=2023,
        escola=escola_com_logs_para_medicao
    )
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem_alimentacao])

    mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        periodo_escolar=periodo_escolar_manha)
    mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        periodo_escolar=periodo_escolar_tarde)
    mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        periodo_escolar=periodo_escolar_noite)
    medicao_programas_projetos = mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        grupo=grupo_programas_e_projetos)
    mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        grupo=grupo_etec)
    mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        grupo=grupo_solicitacoes_alimentacao)

    for dia in range(1, 31):
        mommy.make('DiaCalendario', escola=escola_com_logs_para_medicao, data=f'2023-09-{dia:02d}', dia_letivo=False)
        for nome_campo in ['numero_de_alunos', 'frequencia', 'lanche', 'lanche_4h', 'refeicao', 'repeticao_refeicao',
                           'sobremesa', 'repeticao_sobremesa']:
            mommy.make('ValorMedicao',
                       medicao=medicao_programas_projetos,
                       nome_campo=nome_campo,
                       dia=f'{dia:02d}',
                       categoria_medicao=categoria_medicao,
                       valor='10')
    return solicitacao_medicao


@pytest.fixture
def solicitacao_medicao_inicial_com_grupo(escola, categoria_medicao_dieta_a):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    periodo_manha = mommy.make('PeriodoEscolar', nome='MANHA')
    grupo = mommy.make('GrupoMedicao', nome='Programas e Projetos')
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial',
        uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes=12,
        ano=2022,
        escola=escola
    )
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    medicao = mommy.make(
        'Medicao',
        solicitacao_medicao_inicial=solicitacao_medicao,
        periodo_escolar=periodo_manha,
        grupo=grupo)
    mommy.make('ValorMedicao',
               categoria_medicao=categoria_medicao_dieta_a,
               medicao=medicao,
               nome_campo='frequencia',
               valor='10')
    return solicitacao_medicao


@pytest.fixture
def solicitacoes_medicao_inicial(escola):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    escola_2 = mommy.make('Escola')
    s1 = mommy.make('SolicitacaoMedicaoInicial', mes=6, ano=2022, escola=escola,
                    status='MEDICAO_ENVIADA_PELA_UE')
    s1.tipos_contagem_alimentacao.set([tipo_contagem])

    s2 = mommy.make('SolicitacaoMedicaoInicial', mes=1, ano=2023, escola=escola,
                    status='MEDICAO_ENVIADA_PELA_UE')
    s2.tipos_contagem_alimentacao.set([tipo_contagem])

    s3 = mommy.make('SolicitacaoMedicaoInicial', mes=2, ano=2023, escola=escola,
                    status='MEDICAO_CORRECAO_SOLICITADA')
    s3.tipos_contagem_alimentacao.set([tipo_contagem])

    s4 = mommy.make('SolicitacaoMedicaoInicial', mes=2, ano=2023, escola=escola_2,
                    status='MEDICAO_CORRECAO_SOLICITADA')
    s4.tipos_contagem_alimentacao.set([tipo_contagem])

    s5 = mommy.make('SolicitacaoMedicaoInicial', mes=3, ano=2023, escola=escola,
                    status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE')
    s5.tipos_contagem_alimentacao.set([tipo_contagem])

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
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial', uuid='fb6d1870-a397-4e87-8218-13d316a0ffea',
                                     mes=6, ano=2022, escola=escola)
    solicitacao_medicao.tipos_contagem_alimentacao.set([tipo_contagem])
    return solicitacao_medicao


@pytest.fixture
def anexo_ocorrencia_medicao_inicial(solicitacao_medicao_inicial):
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    return mommy.make('OcorrenciaMedicaoInicial', uuid='1ace193a-6c2c-4686-b9ed-60a922ad0e1a',
                      nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
                      solicitacao_medicao_inicial=solicitacao_medicao_inicial,
                      status='MEDICAO_ENVIADA_PELA_UE')


@pytest.fixture
def anexo_ocorrencia_medicao_inicial_status_aprovado_dre(solicitacao_medicao_inicial):
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    return mommy.make('OcorrenciaMedicaoInicial', uuid='04fb4c1c-0e31-4936-93a7-f2760b968c3b',
                      nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
                      solicitacao_medicao_inicial=solicitacao_medicao_inicial,
                      status='MEDICAO_APROVADA_PELA_DRE')


@pytest.fixture
def anexo_ocorrencia_medicao_inicial_status_inicial():
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial')
    return mommy.make('OcorrenciaMedicaoInicial', uuid='2bed204b-2c1c-4686-b5e3-60a922ad0e1a',
                      nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
                      solicitacao_medicao_inicial=solicitacao_medicao,
                      status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE')


@pytest.fixture
def anexo_ocorrencia_medicao_inicial_status_aprovado_pela_dre():
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    solicitacao_medicao = mommy.make('SolicitacaoMedicaoInicial')
    return mommy.make('OcorrenciaMedicaoInicial', uuid='2bed204b-2c1c-4686-b5e3-60a922ad0e1a',
                      nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
                      solicitacao_medicao_inicial=solicitacao_medicao,
                      status='MEDICAO_APROVADO_PELA_DRE')


@pytest.fixture
def sol_med_inicial_devolvida_pela_dre_para_ue():
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    solicitacao = mommy.make('SolicitacaoMedicaoInicial', status='MEDICAO_CORRECAO_SOLICITADA',
                             uuid='d9de8653-4910-423e-9381-e391c2ae8ecb', com_ocorrencias=True)
    mommy.make('OcorrenciaMedicaoInicial', uuid='ea7299a3-3eb6-4858-a7b4-387446c607a1',
               nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
               solicitacao_medicao_inicial=solicitacao,
               status='MEDICAO_CORRECAO_SOLICITADA')
    return solicitacao


@pytest.fixture
def sol_med_inicial_devolvida_pela_codae_para_ue():
    nome = 'arquivo_teste.pdf'
    arquivo = SimpleUploadedFile(f'arquivo_teste.pdf', bytes('CONTENT', encoding='utf-8'))
    solicitacao = mommy.make('SolicitacaoMedicaoInicial', status='MEDICAO_CORRECAO_SOLICITADA_CODAE',
                             uuid='d9de8653-4910-423e-9381-e391c2ae8ecb', com_ocorrencias=True)
    mommy.make('OcorrenciaMedicaoInicial', uuid='ea7299a3-3eb6-4858-a7b4-387446c607a1',
               nome_ultimo_arquivo=nome, ultimo_arquivo=arquivo,
               solicitacao_medicao_inicial=solicitacao,
               status='MEDICAO_CORRECAO_SOLICITADA_CODAE')
    return solicitacao


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
def medicao_status_inicial(solicitacao_medicao_inicial, periodo_escolar, categoria_medicao):
    medicao = mommy.make('Medicao', periodo_escolar=periodo_escolar, uuid='7041e451-43a7-4d2f-abc6-d0960121d2fb',
                         solicitacao_medicao_inicial=solicitacao_medicao_inicial,
                         status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE')
    valor = 10
    nome_campo = 'observacoes'
    tipo_alimentacao = mommy.make('TipoAlimentacao', nome='Lanche', uuid='0367af8d-26bd-40b5-83d2-9e337622ba50')
    mommy.make('ValorMedicao', valor=valor, nome_campo=nome_campo, medicao=medicao,
               uuid='128f36e2-ea93-4e05-9641-50b0c79ddb5e', dia=22,
               categoria_medicao=categoria_medicao, tipo_alimentacao=tipo_alimentacao)
    return medicao


@pytest.fixture
def medicao_status_enviada_pela_ue(solicitacao_medicao_inicial, periodo_escolar, categoria_medicao):
    medicao = mommy.make('Medicao', periodo_escolar=periodo_escolar, uuid='cbe62cc7-55e9-435d-8c3f-845b6fa20c2e',
                         solicitacao_medicao_inicial=solicitacao_medicao_inicial,
                         status='MEDICAO_ENVIADA_PELA_UE')
    valor = 10
    nome_campo = 'observacoes'
    tipo_alimentacao = mommy.make('TipoAlimentacao', nome='Lanche', uuid='837ed21a-d535-4df2-aa37-f186e4e51392')
    mommy.make('ValorMedicao', valor=valor, nome_campo=nome_campo, medicao=medicao,
               uuid='932d0e67-e434-4071-99dc-b1c4bcdd9310', dia=22,
               categoria_medicao=categoria_medicao, tipo_alimentacao=tipo_alimentacao)
    return medicao


@pytest.fixture
def medicao_aprovada_pela_dre(solicitacao_medicao_inicial, periodo_escolar, categoria_medicao):
    medicao = mommy.make('Medicao', periodo_escolar=periodo_escolar, uuid='65f112a5-8b4b-495b-a29e-1d75fb0b5eeb',
                         solicitacao_medicao_inicial=solicitacao_medicao_inicial, status='MEDICAO_APROVADA_PELA_DRE')
    valor = 20
    nome_campo = 'observacoes'
    tipo_alimentacao = mommy.make('TipoAlimentacao', nome='Lanche', uuid='a5ea11b6-a043-47cd-ba69-d6b207312cbd')
    mommy.make('ValorMedicao', valor=valor, nome_campo=nome_campo, medicao=medicao,
               uuid='0b599490-477f-487b-a49e-c8e7cfdcd00b', dia=25,
               categoria_medicao=categoria_medicao, tipo_alimentacao=tipo_alimentacao)
    return medicao


@pytest.fixture
def categoria_medicao():
    return mommy.make('CategoriaMedicao', nome='ALIMENTAÇÃO', id=1)


@pytest.fixture
def categoria_medicao_dieta_a():
    return mommy.make('CategoriaMedicao', nome='DIETA ESPECIAL - TIPO A')


@pytest.fixture
def categoria_medicao_dieta_a_enteral_aminoacidos():
    return mommy.make('CategoriaMedicao', nome='DIETA ESPECIAL - TIPO A - ENTERAL / RESTRIÇÃO DE AMINOÁCIDOS')


@pytest.fixture
def categoria_medicao_dieta_b():
    return mommy.make('CategoriaMedicao', nome='DIETA ESPECIAL - TIPO B')


@pytest.fixture
def categoria_medicao_solicitacoes_alimentacao():
    return mommy.make('CategoriaMedicao', nome='SOLICITAÇÕES DE ALIMENTAÇÃO')


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
    user = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                 registro_funcional='8888888')
    perfil_cogestor = mommy.make('Perfil',
                                 nome='COGESTOR_DRE',
                                 ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=escola.diretoria_regional,
               perfil=perfil_cogestor,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_da_escola(client, django_user_model, escola):
    email = 'user@escola.com'
    password = 'admin@123'
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR_UE', ativo=True)
    usuario = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                    registro_funcional='123456')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_da_escola_cemei(client, django_user_model, escola_cemei):
    email = 'user@escola.com'
    password = 'admin@123'
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR_UE', ativo=True)
    usuario = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                    registro_funcional='123456')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=escola_cemei, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_adm_da_escola(client, django_user_model, escola):
    email = 'user@escola_adm.com'
    password = 'admin@1234'
    perfil_diretor = mommy.make('Perfil', nome='ADMINISTRADOR_UE', ativo=True)
    usuario = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                    registro_funcional='1234567')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=usuario, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def client_autenticado_codae_medicao(client, django_user_model):
    email = 'codae@medicao.com'
    password = 'admin@1234'
    perfil_medicao = mommy.make('Perfil', nome='ADMINISTRADOR_MEDICAO', ativo=True)
    usuario = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                    registro_funcional='1234588')
    codae = mommy.make('Codae')
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=usuario,
               instituicao=codae,
               perfil=perfil_medicao,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def dia_para_corrigir(categoria_medicao, medicao):
    return mommy.make('DiaParaCorrigir',
                      uuid='d5c33bdc-6c3e-4e70-a7f4-60603362f386',
                      medicao=medicao,
                      categoria_medicao=categoria_medicao,
                      dia='01')
