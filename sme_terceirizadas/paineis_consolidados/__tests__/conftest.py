import datetime

import pytest
import pytz
from faker import Faker
from model_mommy import mommy

from ..models import SolicitacoesEscola
from ...cardapio.models import AlteracaoCardapio
from ...dados_comuns.models import TemplateMensagem
from ...inclusao_alimentacao.models import InclusaoAlimentacaoContinua
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
    return mommy.make('Escola', diretoria_regional=diretoria_regional2, lote=lote)


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
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)
    perfil_professor = mommy.make('Perfil', nome='ADMINISTRADOR_ESCOLA', ativo=False,
                                  uuid='48330a6f-c444-4462-971e-476452b328b2')
    perfil_diretor = mommy.make('Perfil', nome='DIRETOR', ativo=True, uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')

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
    user_dre = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    user_codae = django_user_model.objects.create_user(password='xxx2', email='xxx@email.com',
                                                       registro_funcional='9987634', cpf='12oiu3123')
    user_escola = django_user_model.objects.create_user(password='xxx', email='user@escola.com',
                                                        registro_funcional='123123', cpf='12312312332')
    client.login(email=email, password=password)

    perfil_adm_dre = mommy.make('Perfil', nome='ADMINISTRADOR_DRE', ativo=True)

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


@pytest.fixture(params=[
    # data evento
    (datetime.date(datetime.datetime.now().year, 10, 1)),
    (datetime.date(datetime.datetime.now().year, 10, 2)),
    (datetime.date(datetime.datetime.now().year, 10, 29)),
    (datetime.date(datetime.datetime.now().year, 10, 30))
])
def solicitacoes_escola_params(escola, request):
    data_evento = request.param
    mommy.make(AlteracaoCardapio,
               escola=escola,
               data_inicial=data_evento,
               status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR)
    return SolicitacoesEscola.objects.all()


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
