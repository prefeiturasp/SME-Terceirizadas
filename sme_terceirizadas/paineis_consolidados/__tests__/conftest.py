import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from ...cardapio.models import AlteracaoCardapio
from ...dados_comuns.models import TemplateMensagem
from ...inclusao_alimentacao.models import InclusaoAlimentacaoContinua
from ...kit_lanche.models import KitLanche, SolicitacaoKitLanche, SolicitacaoKitLancheAvulsa
from ..models import SolicitacoesEscola

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def escola():
    lote = mommy.make('Lote')
    return mommy.make('Escola', lote=lote, uuid='fdf23c84-c9ff-4811-adff-e70df5378466')


@pytest.fixture
def templates():
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.ALTERACAO_CARDAPIO)
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.SOLICITACAO_KIT_LANCHE_AVULSA)
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO_CONTINUA)


@pytest.fixture
def alteracoes_cardapio(escola):
    alteracao_cardapio_1 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      data_inicial=datetime.date(2019, 10, 1))
    alteracao_cardapio_2 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      data_inicial=datetime.date(2019, 10, 10))
    alteracao_cardapio_3 = mommy.make(AlteracaoCardapio,
                                      escola=escola,
                                      data_inicial=datetime.date(2019, 10, 20))
    return alteracao_cardapio_1, alteracao_cardapio_2, alteracao_cardapio_3


@pytest.fixture
def solicitacoes_kit_lanche(escola):
    kits = mommy.make(KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits, data=datetime.date(2019, 1, 1))
    solicitacao_kit_lanche_avulsa_1 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits, data=datetime.date(2019, 2, 1))
    solicitacao_kit_lanche_avulsa_2 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits, data=datetime.date(2018, 2, 1))
    solicitacao_kit_lanche_avulsa_3 = mommy.make(SolicitacaoKitLancheAvulsa,
                                                 local=fake.text()[:160],
                                                 quantidade_alunos=300,
                                                 solicitacao_kit_lanche=solicitacao_kit_lanche,
                                                 escola=escola)
    solicitacao_kit_lanche = mommy.make(SolicitacaoKitLanche, kits=kits, data=datetime.date(2020, 2, 1))
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
                                     escola=escola)
    inclusao_continua_2 = mommy.make(InclusaoAlimentacaoContinua,
                                     data_inicial=datetime.date(2019, 6, 1),
                                     data_final=datetime.date(2019, 7, 1),
                                     escola=escola)
    inclusao_continua_3 = mommy.make(InclusaoAlimentacaoContinua,
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
