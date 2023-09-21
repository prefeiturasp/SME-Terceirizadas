import datetime

import pytest
import pytz
from faker import Faker
from freezegun import freeze_time
from model_mommy import mommy

from ...cardapio.models import AlteracaoCardapio, SuspensaoAlimentacaoDaCEI
from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ...dados_comuns.models import TemplateMensagem
from ...dieta_especial.models import SolicitacaoDietaEspecial
from ...inclusao_alimentacao.models import (
    DiasMotivosInclusaoDeAlimentacaoCEI,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI
)
from ...kit_lanche.models import KitLanche, SolicitacaoKitLanche, SolicitacaoKitLancheAvulsa

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def diretoria_regional():
    return mommy.make('DiretoriaRegional')


@pytest.fixture
def escola(diretoria_regional):
    lote = mommy.make('Lote')
    return mommy.make('Escola', diretoria_regional=diretoria_regional, lote=lote,
                      uuid='fdf23c84-c9ff-4811-adff-e70df5378466')


@pytest.fixture
def diretoria_regional2():
    return mommy.make('DiretoriaRegional')


@pytest.fixture
def escola2(diretoria_regional2):
    lote = mommy.make('Lote')
    contato = mommy.make('dados_comuns.Contato', nome='FULANO', email='fake@email.com')
    return mommy.make('Escola', diretoria_regional=diretoria_regional2, lote=lote, contato=contato)


@pytest.fixture
def templates():
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.ALTERACAO_CARDAPIO)
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.SOLICITACAO_KIT_LANCHE_AVULSA)
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO_CONTINUA)


@pytest.fixture
def alteracoes_cardapio(escola):
    alteracao_cardapio_1 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      criado_em=datetime.date(2019, 10, 1),
                                      data_inicial=datetime.date(2019, 10, 1))
    alteracao_cardapio_2 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      criado_em=datetime.date(2019, 10, 10),
                                      data_inicial=datetime.date(2019, 10, 10))
    alteracao_cardapio_3 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      criado_em=datetime.date(2019, 10, 20),
                                      data_inicial=datetime.date(2019, 10, 20))
    return alteracao_cardapio_1, alteracao_cardapio_2, alteracao_cardapio_3


@pytest.fixture
def solicitacoes_kit_lanche(escola):
    kits = mommy.make(KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        criado_em=datetime.date(2019, 1, 1),
                                        data=datetime.date(2019, 1, 1)
                                        )
    solicitacao_kit_lanche_avulsa_1 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        data=datetime.date(2019, 2, 1),
                                        criado_em=datetime.date(2019, 2, 1)
                                        )
    solicitacao_kit_lanche_avulsa_2 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        data=datetime.date(2018, 2, 1),
                                        criado_em=datetime.date(2019, 2, 1),
                                        )
    solicitacao_kit_lanche_avulsa_3 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        criado_em=datetime.date(2019, 2, 1),
                                        data=datetime.date(2020, 2, 1)
                                        )
    solicitacao_kit_lanche_avulsa_4 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    return (solicitacao_kit_lanche_avulsa_1, solicitacao_kit_lanche_avulsa_2, solicitacao_kit_lanche_avulsa_3,
            solicitacao_kit_lanche_avulsa_4)


@pytest.fixture
def inclusoes_de_alimentacao_continua(escola):
    inclusao_continua_1 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 5, 1),
                                     data_final=datetime.date(2019, 6, 1),
                                     criado_em=datetime.date(2019, 5, 1),
                                     escola=escola)
    inclusao_continua_2 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 6, 1),
                                     criado_em=datetime.date(2019, 6, 1),
                                     data_final=datetime.date(2019, 7, 1),
                                     escola=escola)
    inclusao_continua_3 = mommy.make(InclusaoAlimentacaoContinua,
                                     criado_em=datetime.date(2019, 7, 1),
                                     data_inicial=datetime.date(2019, 7, 1),
                                     data_final=datetime.date(2019, 8, 1),
                                     escola=escola)
    return inclusao_continua_1, inclusao_continua_2, inclusao_continua_3


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('diretor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('diretor_2@sme.prefeitura.sp.gov.br', 'aasdsadsadff', '0000002', '56789925031'),
    ('diretor_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('diretor_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('diretor_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0005551', '40296233013')
])
def users_diretor_escola(client, django_user_model, request, escola, templates, alteracoes_cardapio,
                         solicitacoes_kit_lanche, inclusoes_de_alimentacao_continua):
    email, password, rf, cpf = request.param
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional=rf, cpf=cpf)
    client.login(username=email, password=password)
    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_UE', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR_UE', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_professor,
               ativo=False, data_inicial=hoje, data_final=hoje + datetime.timedelta(days=30)
               )  # finalizado
    mommy.make('Vinculo', usuario=user, instituicao=escola, perfil=perfil_diretor,
               data_inicial=hoje, ativo=True)
    alt1, alt2, alt3 = alteracoes_cardapio
    alt1.inicia_fluxo(user=user)

    alt2.inicia_fluxo(user=user)
    alt3.inicia_fluxo(user=user)
    solkit1, solkit2, solkit3, solkit4 = solicitacoes_kit_lanche
    solkit1.inicia_fluxo(user=user)
    solkit2.inicia_fluxo(user=user)
    solkit3.inicia_fluxo(user=user)
    solkit4.inicia_fluxo(user=user)
    inc_continua_1, inc_continua_2, inc_continua_3 = inclusoes_de_alimentacao_continua
    inc_continua_1.inicia_fluxo(user=user)
    inc_continua_2.inicia_fluxo(user=user)
    inc_continua_3.inicia_fluxo(user=user)

    inc_continua_1.criado_em = datetime.datetime(year=2019, month=1, day=15, tzinfo=pytz.UTC)
    inc_continua_1.save()
    inc_continua_2.criado_em = datetime.datetime(year=2019, month=2, day=15, tzinfo=pytz.UTC)
    inc_continua_2.save()
    inc_continua_3.criado_em = datetime.datetime(year=2019, month=3, day=15, tzinfo=pytz.UTC)
    inc_continua_3.save()

    k1 = solkit1.solicitacao_kit_lanche
    k1.criado_em = datetime.datetime(year=2019, month=4, day=15, tzinfo=pytz.UTC)
    k1.save()
    k2 = solkit2.solicitacao_kit_lanche
    k2.criado_em = datetime.datetime(year=2019, month=5, day=15, tzinfo=pytz.UTC)
    k2.save()
    k3 = solkit3.solicitacao_kit_lanche
    k3.criado_em = datetime.datetime(year=2019, month=6, day=15, tzinfo=pytz.UTC)
    k3.save()
    k4 = solkit4.solicitacao_kit_lanche
    k4.criado_em = datetime.datetime(year=2019, month=7, day=15, tzinfo=pytz.UTC)
    k4.save()

    alt1.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt1.save()
    alt2.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt2.save()
    alt3.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt3.save()

    return client, email, password, rf, cpf, user


@pytest.fixture
def alteracoes_cardapio_dre(escola2):
    alteracao_cardapio_1 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 3, 1),
                                      data_inicial=datetime.date(2019, 3, 1))
    alteracao_cardapio_2 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 2, 10),
                                      data_inicial=datetime.date(2019, 2, 10))
    alteracao_cardapio_3 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 1, 20),
                                      data_inicial=datetime.date(2019, 1, 20))
    return alteracao_cardapio_1, alteracao_cardapio_2, alteracao_cardapio_3


@freeze_time('2020-02-03')  # Segunda
@pytest.fixture
def alteracoes_cardapio_dre_atual(escola2):
    alteracao_cardapio_1 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 3, 1),
                                      data_inicial=datetime.date.today() + datetime.timedelta(days=1))
    alteracao_cardapio_2 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 2, 10),
                                      data_inicial=datetime.date.today() + datetime.timedelta(days=5))
    alteracao_cardapio_3 = mommy.make(AlteracaoCardapio,
                                      escola=escola2,
                                      criado_em=datetime.date(2019, 1, 20),
                                      data_inicial=datetime.date.today() + datetime.timedelta(days=20))
    return alteracao_cardapio_1, alteracao_cardapio_2, alteracao_cardapio_3


@pytest.fixture
def solicitacoes_kit_lanche_dre(escola2):
    kits = mommy.make(KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        criado_em=datetime.date(2019, 5, 1),
                                        data=datetime.date(2019, 5, 1)
                                        )
    solicitacao_kit_lanche_avulsa_1 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola2)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        data=datetime.date(2019, 2, 1),
                                        criado_em=datetime.date(2019, 2, 1)
                                        )
    solicitacao_kit_lanche_avulsa_2 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola2)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        data=datetime.date(2018, 2, 1),
                                        criado_em=datetime.date(2019, 2, 1),
                                        )
    solicitacao_kit_lanche_avulsa_3 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola2)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits,
                                        criado_em=datetime.date(2019, 7, 1),
                                        data=datetime.date(2020, 7, 1)
                                        )
    solicitacao_kit_lanche_avulsa_4 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola2)
    return (solicitacao_kit_lanche_avulsa_1, solicitacao_kit_lanche_avulsa_2, solicitacao_kit_lanche_avulsa_3,
            solicitacao_kit_lanche_avulsa_4)


@pytest.fixture
def inclusoes_de_alimentacao_continua_dre(escola2):
    inclusao_continua_1 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 5, 1),
                                     data_final=datetime.date(2019, 6, 1),
                                     escola=escola2)
    inclusao_continua_2 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 6, 1),
                                     data_final=datetime.date(2019, 7, 1),
                                     escola=escola2)
    inclusao_continua_3 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 12, 1),
                                     data_final=datetime.date(2019, 12, 9),
                                     escola=escola2)
    return inclusao_continua_1, inclusao_continua_2, inclusao_continua_3


@pytest.fixture(params=[
    # email, senha, rf, cpf
    ('DREADM_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052'),
    ('DREADM_2@sme.prefeitura.sp.gov.br', 'aasdsadsadff', '0000002', '56789925031'),
    ('DREADM_3@sme.prefeitura.sp.gov.br', '98as7d@@#', '0000147', '86880963099'),
    ('DREADM_4@sme.prefeitura.sp.gov.br', '##$$csazd@!', '0000441', '13151715036'),
    ('DREADM_5@sme.prefeitura.sp.gov.br', '!!@##FFG121', '0005551', '40296233013')
])
def solicitacoes_ano_dre(client, django_user_model, request, diretoria_regional2, templates, alteracoes_cardapio_dre,
                         solicitacoes_kit_lanche_dre, inclusoes_de_alimentacao_continua_dre):
    email, password, rf, cpf = request.param
    user_dre = django_user_model.objects.create_user(username=email, password=password, email=email,
                                                     registro_funcional=rf, cpf=cpf)
    user_codae = django_user_model.objects.create_user(username='xxx@email.com',
                                                       password=constants.DJANGO_ADMIN_PASSWORD,
                                                       email='xxx@email.com', registro_funcional='9987634',
                                                       cpf='12oiu3123')
    user_escola = django_user_model.objects.create_user(username='user@escola.com',
                                                        password=constants.DJANGO_ADMIN_PASSWORD,
                                                        email='user@escola.com', registro_funcional='123123',
                                                        cpf='12312312332')
    client.login(username=email, password=password)

    perfil_adm_dre = mommy.make('Perfil', nome='COGESTOR_DRE', ativo=True)

    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user_dre, instituicao=diretoria_regional2, perfil=perfil_adm_dre,
               data_inicial=hoje, ativo=True)

    alt1, alt2, alt3 = alteracoes_cardapio_dre
    alt1.inicia_fluxo(user=user_escola)
    alt2.inicia_fluxo(user=user_escola)
    alt3.inicia_fluxo(user=user_escola)
    solkit1, solkit2, solkit3, solkit4 = solicitacoes_kit_lanche_dre
    solkit1.inicia_fluxo(user=user_escola)
    solkit2.inicia_fluxo(user=user_escola)
    solkit3.inicia_fluxo(user=user_escola)
    solkit4.inicia_fluxo(user=user_escola)

    inc_continua_1, inc_continua_2, inc_continua_3 = inclusoes_de_alimentacao_continua_dre
    inc_continua_1.inicia_fluxo(user=user_escola)
    inc_continua_2.inicia_fluxo(user=user_escola)
    inc_continua_3.inicia_fluxo(user=user_escola)

    inc_continua_1.criado_em = datetime.datetime(year=2019, month=1, day=15, tzinfo=pytz.UTC)
    inc_continua_1.save()
    inc_continua_2.criado_em = datetime.datetime(year=2019, month=1, day=15, tzinfo=pytz.UTC)
    inc_continua_2.save()
    inc_continua_3.criado_em = datetime.datetime(year=2019, month=1, day=15, tzinfo=pytz.UTC)
    inc_continua_3.save()

    k1 = solkit1.solicitacao_kit_lanche
    k1.criado_em = datetime.datetime(year=2019, month=2, day=15, tzinfo=pytz.UTC)
    k1.save()
    k2 = solkit2.solicitacao_kit_lanche
    k2.criado_em = datetime.datetime(year=2019, month=2, day=15, tzinfo=pytz.UTC)
    k2.save()
    k3 = solkit3.solicitacao_kit_lanche
    k3.criado_em = datetime.datetime(year=2019, month=4, day=15, tzinfo=pytz.UTC)
    k3.save()
    k4 = solkit4.solicitacao_kit_lanche
    k4.criado_em = datetime.datetime(year=2019, month=4, day=15, tzinfo=pytz.UTC)
    k4.save()

    alt1.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt1.save()
    alt2.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt2.save()
    alt3.criado_em = datetime.datetime(year=2019, month=12, day=15, tzinfo=pytz.UTC)
    alt3.save()

    alt1, alt2, alt3 = alteracoes_cardapio_dre
    alt1.dre_valida(user=user_dre)
    alt2.dre_valida(user=user_dre)
    alt3.dre_valida(user=user_dre)
    solkit1, solkit2, solkit3, solkit4 = solicitacoes_kit_lanche_dre
    solkit1.dre_valida(user=user_dre)
    solkit2.dre_valida(user=user_dre)
    solkit3.dre_valida(user=user_dre)
    solkit4.dre_valida(user=user_dre)
    inc_continua_1, inc_continua_2, inc_continua_3 = inclusoes_de_alimentacao_continua_dre
    inc_continua_1.dre_valida(user=user_dre)
    inc_continua_2.dre_valida(user=user_dre)
    inc_continua_3.dre_valida(user=user_dre)
    inc_continua_1.codae_nega(user=user_codae)
    return client, email, password, rf, cpf, user_dre


@pytest.fixture
def client_autenticado_painel_consolidados(client_autenticado, django_user_model):
    user = django_user_model.objects.get(email='test@test.com')
    diretoria_regional = mommy.make('escola.DiretoriaRegional',
                                    usuarios=[user],
                                    make_m2m=True
                                    )
    escola = mommy.make('escola.Escola', diretoria_regional=diretoria_regional)
    mommy.make(AlteracaoCardapio,
               escola=escola,
               status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR)
    return client_autenticado


@pytest.fixture
def solicitacoes_dieta_especial():
    statuses = [
        DietaEspecialWorkflow.CODAE_A_AUTORIZAR,
        DietaEspecialWorkflow.CODAE_AUTORIZADO,
        DietaEspecialWorkflow.CODAE_NEGOU_PEDIDO
    ]
    saida = []

    for status in statuses:
        saida += mommy.make(SolicitacaoDietaEspecial,
                            status=status,
                            _quantity=2)

    return saida


@pytest.fixture(params=[
    [DietaEspecialWorkflow.CODAE_A_AUTORIZAR, 'pendentes-autorizacao'],
    [DietaEspecialWorkflow.CODAE_AUTORIZADO, 'autorizados'],
    [DietaEspecialWorkflow.CODAE_NEGOU_PEDIDO, 'negados'],
])
def status_and_endpoint(request):
    return request.param


@pytest.fixture
def client_autenticado_dre_paineis_consolidados(client, django_user_model, diretoria_regional2, templates,
                                                alteracoes_cardapio_dre_atual):
    email = 'test@test.com'
    email2 = 'user@escola.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional='8888888')
    user_escola = django_user_model.objects.create_user(username=email2, password=password, email=email2,
                                                        registro_funcional='123123', cpf='12312312332')
    perfil_cogestor = mommy.make('Perfil',
                                 nome=constants.COGESTOR_DRE,
                                 ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=diretoria_regional2,
               perfil=perfil_cogestor,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    alt1, alt2, alt3 = alteracoes_cardapio_dre_atual
    alt1.inicia_fluxo(user=user_escola)
    alt2.inicia_fluxo(user=user_escola)
    alt3.inicia_fluxo(user=user_escola)
    return client


@pytest.fixture
def motivo_inclusao_normal():
    return mommy.make('MotivoInclusaoNormal', nome=fake.name())


@pytest.fixture
def periodo_escolar_manha():
    return mommy.make('PeriodoEscolar', nome='MANHA')


@pytest.fixture
def tipo_alimentacao_refeicao():
    return mommy.make('TipoAlimentacao', nome='Refeição')


@pytest.fixture
def tipo_alimentacao_lanche():
    return mommy.make('TipoAlimentacao', nome='Lanche')


@pytest.fixture
def inclusoes_normais(escola, motivo_inclusao_normal, periodo_escolar_manha, tipo_alimentacao_refeicao,
                      tipo_alimentacao_lanche):
    grupo_inclusao_normal = mommy.make(
        'GrupoInclusaoAlimentacaoNormal',
        escola=escola,
        status='CODAE_AUTORIZADO',
        rastro_escola=escola,
        rastro_dre=escola.diretoria_regional)
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=grupo_inclusao_normal.uuid,
               status_evento=1,
               solicitacao_tipo=4)
    mommy.make('InclusaoAlimentacaoNormal',
               data=datetime.date(2023, 7, 1),
               grupo_inclusao=grupo_inclusao_normal)
    mommy.make('InclusaoAlimentacaoNormal',
               data=datetime.date(2023, 7, 2),
               motivo=motivo_inclusao_normal,
               grupo_inclusao=grupo_inclusao_normal)
    qp = mommy.make('QuantidadePorPeriodo',
                    numero_alunos=100,
                    periodo_escolar=periodo_escolar_manha,
                    grupo_inclusao_normal=grupo_inclusao_normal)
    qp.tipos_alimentacao.add(tipo_alimentacao_lanche)
    qp.tipos_alimentacao.add(tipo_alimentacao_refeicao)
    qp.save()


@pytest.fixture
def solicitacao_medicao_inicial(escola, periodo_escolar_manha):
    tipo_contagem = mommy.make('TipoContagemAlimentacao', nome='Fichas')
    solicitacao_medicao = mommy.make(
        'SolicitacaoMedicaoInicial',
        uuid='bed4d779-2d57-4c5f-bf9c-9b93ddac54d9',
        mes='08',
        ano='2023',
        escola=escola,
        tipo_contagem_alimentacoes=tipo_contagem
    )
    medicao = mommy.make('Medicao', solicitacao_medicao_inicial=solicitacao_medicao,
                         periodo_escolar=periodo_escolar_manha)
    mommy.make('ValorMedicao', medicao=medicao)
    return solicitacao_medicao


@pytest.fixture
def client_autenticado_escola_paineis_consolidados(client, django_user_model, escola, templates, inclusoes_normais,
                                                   solicitacao_medicao_inicial):
    email = 'test@test.com'
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(username=email, password=password,
                                                 email=email, registro_funcional='8888888')
    perfil_diretor = mommy.make('Perfil', nome=constants.DIRETOR_UE, ativo=True)
    hoje = datetime.date.today()
    mommy.make('Vinculo',
               usuario=user,
               instituicao=escola,
               perfil=perfil_diretor,
               data_inicial=hoje,
               ativo=True)
    client.login(username=email, password=password)
    return client


@pytest.fixture
def inclusao_alimentacao_continua(escola, periodo_escolar_manha):
    data_inicial = datetime.date(2023, 5, 20)
    data_final = datetime.date(2023, 6, 10)
    inclusao_continua = mommy.make(InclusaoAlimentacaoContinua,
                                   data_inicial=data_inicial,
                                   data_final=data_final,
                                   escola=escola,
                                   rastro_escola=escola,
                                   status='CODAE_AUTORIZADO')
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=inclusao_continua.uuid,
               status_evento=1,
               solicitacao_tipo=7)
    mommy.make('QuantidadePorPeriodo',
               numero_alunos=50,
               inclusao_alimentacao_continua=inclusao_continua,
               periodo_escolar=periodo_escolar_manha)


@pytest.fixture
def periodo_escolar_integral():
    return mommy.make('PeriodoEscolar', nome='INTEGRAL')


@pytest.fixture()
def inclusao_alimentacao_cei(motivo_inclusao_normal, escola, periodo_escolar_manha, periodo_escolar_integral):
    inclusao_cei = mommy.make(InclusaoAlimentacaoDaCEI,
                              escola=escola,
                              rastro_escola=escola,
                              periodo_escolar=periodo_escolar_manha,
                              status='CODAE_AUTORIZADO')
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=inclusao_cei.uuid,
               status_evento=1,
               solicitacao_tipo=5)
    mommy.make(DiasMotivosInclusaoDeAlimentacaoCEI,
               inclusao_cei=inclusao_cei,
               motivo=motivo_inclusao_normal,
               data=datetime.date(2023, 8, 10))
    faixa_etaria = mommy.make('FaixaEtaria', inicio=48, fim=73, ativo=True)
    mommy.make(QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI,
               inclusao_alimentacao_da_cei=inclusao_cei,
               faixa_etaria=faixa_etaria,
               quantidade_alunos=25,
               periodo=periodo_escolar_manha,
               periodo_externo=periodo_escolar_integral)
    return inclusao_cei


@pytest.fixture
def motivo_suspensao():
    return mommy.make('MotivoSuspensao', nome=fake.name())


@pytest.fixture()
def suspensoes_alimentacao(motivo_suspensao, escola, periodo_escolar_manha, periodo_escolar_integral,
                           tipo_alimentacao_lanche, tipo_alimentacao_refeicao):
    suspensao_cei = mommy.make(SuspensaoAlimentacaoDaCEI,
                               escola=escola,
                               rastro_escola=escola,
                               motivo=motivo_suspensao,
                               status='INFORMADO',
                               data=datetime.date(2023, 7, 15))
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=suspensao_cei.uuid,
               status_evento=0,
               solicitacao_tipo=6)
    suspensao_cei.periodos_escolares.add(periodo_escolar_manha)
    suspensao_cei.periodos_escolares.add(periodo_escolar_integral)
    suspensao_cei.save()

    grupo_suspensao_alimentacao = mommy.make(
        'GrupoSuspensaoAlimentacao',
        escola=escola,
        status='INFORMADO',
        rastro_escola=escola,
        rastro_dre=escola.diretoria_regional)
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=grupo_suspensao_alimentacao.uuid,
               status_evento=1,
               solicitacao_tipo=2)
    mommy.make('SuspensaoAlimentacao',
               data=datetime.date(2023, 8, 3),
               motivo=motivo_suspensao,
               grupo_suspensao=grupo_suspensao_alimentacao)
    mommy.make('SuspensaoAlimentacao',
               data=datetime.date(2023, 8, 13),
               motivo=motivo_suspensao,
               grupo_suspensao=grupo_suspensao_alimentacao)
    qp_suspensao_manha = mommy.make('QuantidadePorPeriodoSuspensaoAlimentacao',
                                    numero_alunos=75,
                                    periodo_escolar=periodo_escolar_manha,
                                    grupo_suspensao=grupo_suspensao_alimentacao)
    qp_suspensao_manha.tipos_alimentacao.add(tipo_alimentacao_lanche)
    qp_suspensao_manha.tipos_alimentacao.add(tipo_alimentacao_refeicao)
    qp_suspensao_manha.save()
    qp_suspensao_integral = mommy.make('QuantidadePorPeriodoSuspensaoAlimentacao',
                                       numero_alunos=50,
                                       periodo_escolar=periodo_escolar_integral,
                                       grupo_suspensao=grupo_suspensao_alimentacao)
    qp_suspensao_integral.tipos_alimentacao.add(tipo_alimentacao_lanche)
    qp_suspensao_integral.tipos_alimentacao.add(tipo_alimentacao_refeicao)
    qp_suspensao_integral.save()

    return suspensao_cei, grupo_suspensao_alimentacao
