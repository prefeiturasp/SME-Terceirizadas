import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def kit_lanche():
    itens = mommy.make(models.ItemKitLanche,
                       nome=fake.name(),
                       _quantity=3)
    return mommy.make(models.KitLanche, nome=fake.name(),
                      itens=itens)


@pytest.fixture
def item_kit_lanche():
    return mommy.make(models.ItemKitLanche,
                      nome=fake.name())


@pytest.fixture
def solicitacao_avulsa():
    dado_base = mommy.make(models.SolicitacaoKitLanche, )
    escola = mommy.make('escola.Escola')
    return mommy.make(models.SolicitacaoKitLancheAvulsa,
                      local=fake.text(),
                      quantidade_alunos=999,
                      dado_base=dado_base,
                      escola=escola)


@pytest.fixture
def solicitacao_unificada():
    motivo = mommy.make(models.MotivoSolicitacaoUnificada, nome=fake.name())
    dado_base = mommy.make(models.SolicitacaoKitLanche, )
    dre = mommy.make('escola.DiretoriaRegional')
    return mommy.make(models.SolicitacaoKitLancheUnificada,
                      local=fake.text(),
                      quantidade_max_alunos_por_escola=999,
                      lista_kit_lanche_igual=True,
                      dado_base=dado_base,
                      outro_motivo=fake.text(),
                      diretoria_regional=dre,
                      motivo=motivo)


@pytest.fixture
def solicitacao():
    kits = mommy.make(models.KitLanche, nome=fake.name(), _quantity=3)
    return mommy.make(models.SolicitacaoKitLanche,
                      descricao=fake.text(),
                      motivo=fake.text(),
                      tempo_passeio=models.SolicitacaoKitLanche.CINCO_A_SETE,
                      kits=kits)


@pytest.fixture(params=[
    (0, True),
    (1, True),
    (2, True),
])
def horarios_passeio(request):
    return request.param


erro_esperado_passeio = 'tempo de passeio deve ser qualquer uma das opções:'


@pytest.fixture(params=[
    ('0', erro_esperado_passeio),
    ('TESTE', erro_esperado_passeio),
])
def horarios_passeio_invalido(request):
    return request.param
