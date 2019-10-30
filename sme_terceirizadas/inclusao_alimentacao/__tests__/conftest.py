import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import TemplateMensagem

fake = Faker('pt-Br')
fake.seed(420)


@pytest.fixture
def escola():
    lote = mommy.make('Lote')
    return mommy.make('Escola', lote=lote)


@pytest.fixture
def motivo_inclusao_continua():
    return mommy.make(models.MotivoInclusaoContinua, nome='teste nome')


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


@pytest.fixture(params=[
    # data ini, data fim, esperado
    (datetime.date(2019, 10, 1), datetime.date(2019, 10, 30), datetime.date(2019, 10, 1)),
    (datetime.date(2019, 10, 1), datetime.date(2019, 9, 20), datetime.date(2019, 9, 20))
]
)
def inclusao_alimentacao_continua_params(escola, motivo_inclusao_continua, request):
    mommy.make(TemplateMensagem, assunto='TESTE',
               tipo=TemplateMensagem.INCLUSAO_ALIMENTACAO_CONTINUA,
               template_html='@id @criado_em @status @link')
    data_inicial, data_final, esperado = request.param
    model = mommy.make(models.InclusaoAlimentacaoContinua,
                       uuid='98dc7cb7-7a38-408d-907c-c0f073ca2d13',
                       motivo=motivo_inclusao_continua,
                       data_inicial=data_inicial,
                       data_final=data_final,
                       outro_motivo=fake.name(),
                       escola=escola)
    return model, esperado


@pytest.fixture(params=[
    # data_inicial, data_final
    (datetime.date(2019, 10, 4), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 5), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 6), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 7), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 8), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 9), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 10), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 11), datetime.date(2019, 12, 31)),
])
def inclusao_alimentacao_continua_parametros_semana(request):
    return request.param


@pytest.fixture(params=[
    # data_inicial, data_final
    (datetime.date(2019, 10, 4), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 5), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 10), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 20), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 25), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 10, 31), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 11, 3), datetime.date(2019, 12, 31)),
    (datetime.date(2019, 11, 4), datetime.date(2019, 12, 31)),
])
def inclusao_alimentacao_continua_parametros_mes(request):
    return request.param


@pytest.fixture(params=[
    # data_inicial, data_final, status
    (datetime.date(2019, 10, 3), datetime.date(2019, 12, 31), PedidoAPartirDaEscolaWorkflow.RASCUNHO),
    (datetime.date(2019, 10, 2), datetime.date(2019, 12, 31), PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR),
    (datetime.date(2019, 10, 1), datetime.date(2019, 12, 31), PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO),
    (datetime.date(2019, 10, 1), datetime.date(2019, 12, 31), PedidoAPartirDaEscolaWorkflow.DRE_PEDIU_ESCOLA_REVISAR),
])
def inclusao_alimentacao_continua_parametros_vencidos(request):
    return request.param


@pytest.fixture(params=[
    # data_inicial, data_final, dias semana,
    (datetime.date(2019, 10, 20), datetime.date(2019, 10, 30), [1, 2, 3, 4, 5, 6]),
    (datetime.date(2019, 10, 17), datetime.date(2020, 10, 30), [1, 2, 3]),
    (datetime.date(2020, 1, 1), datetime.date(2020, 2, 28), [1, 2, 3, 4]),
    (datetime.date(2019, 10, 17), datetime.date(2020, 12, 30), [1, 4])
])
def inclusao_alimentacao_continua_parametros(request):
    return request.param


@pytest.fixture
def motivo_inclusao_normal_nome():
    return mommy.make(models.MotivoInclusaoNormal, nome='Passeio 5h')


@pytest.fixture
def grupo_inclusao_alimentacao_nome():
    return mommy.make(models.GrupoInclusaoAlimentacaoNormal)
