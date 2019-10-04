import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ...dados_comuns.models import TemplateMensagem

fake = Faker('pt-Br')
fake.seed(420)


@pytest.fixture
def motivo_inclusao_continua():
    return mommy.make(models.MotivoInclusaoContinua, nome=fake.name())


@pytest.fixture
def motivo_inclusao_normal():
    return mommy.make(models.MotivoInclusaoNormal, nome=fake.name())


@pytest.fixture
def quantidade_por_periodo():
    periodo_escolar = mommy.make('escola.PeriodoEscolar')
    tipos_alimentacao = mommy.make('cardapio.TipoAlimentacao', _quantity=5, make_m2m=True)
    return mommy.make(models.QuantidadePorPeriodo,
                      numero_alunos=0,
                      periodo_escolar=periodo_escolar,
                      tipos_alimentacao=tipos_alimentacao
                      )


@pytest.fixture
def inclusao_alimentacao_continua():
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO_CONTINUA,
               template_html='@id @criado_em @status @link')
    motivo = mommy.make(models.MotivoInclusaoContinua, nome=fake.name())
    escola = mommy.make('escola.Escola')
    return mommy.make(models.InclusaoAlimentacaoContinua,
                      uuid='98dc7cb7-7a38-408d-907c-c0f073ca2d13',
                      motivo=motivo,
                      outro_motivo=fake.name(),
                      escola=escola)


@pytest.fixture(params=[
    # data_inicial, data_final
    ((2019, 10, 4), (2019, 12, 31)),
    ((2019, 10, 5), (2019, 12, 31)),
    ((2019, 10, 6), (2019, 12, 31)),
    ((2019, 10, 7), (2019, 12, 31)),
    ((2019, 10, 8), (2019, 12, 31)),
    ((2019, 10, 9), (2019, 12, 31)),
    ((2019, 10, 10), (2019, 12, 31)),
    ((2019, 10, 11), (2019, 12, 31)),
])
def inclusao_alimentacao_continua_parametros_semana(request):
    return request.param


@pytest.fixture(params=[
    # data_inicial, data_final
    ((2019, 10, 4), (2019, 12, 31)),
    ((2019, 10, 5), (2019, 12, 31)),
    ((2019, 10, 10), (2019, 12, 31)),
    ((2019, 10, 20), (2019, 12, 31)),
    ((2019, 10, 25), (2019, 12, 31)),
    ((2019, 10, 31), (2019, 12, 31)),
    ((2019, 11, 3), (2019, 12, 31)),
    ((2019, 11, 4), (2019, 12, 31)),
])
def inclusao_alimentacao_continua_parametros_mes(request):
    return request.param
