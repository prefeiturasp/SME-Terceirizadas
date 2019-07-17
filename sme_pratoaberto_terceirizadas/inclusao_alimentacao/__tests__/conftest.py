import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

fake = Faker('pt-Br')
fake.seed(420)


@pytest.fixture
def motivo_inclusao_continua():
    return mommy.make(models.MotivoInclusaoContinua, nome=fake.name())


@pytest.fixture
def motivo_inclusao_normal():
    # TODO: dando erro com fake.name por que?
    return mommy.make(models.MotivoInclusaoNormal, nome='TESTE')


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
    motivo = mommy.make(models.MotivoInclusaoContinua, nome=fake.name())
    escola = mommy.make('escola.Escola')
    quantidades_periodo = mommy.make(models.QuantidadePorPeriodo, _quantity=419, make_m2m=True)
    return mommy.make(models.InclusaoAlimentacaoContinua,
                      motivo=motivo,
                      outro_motivo=fake.name(),
                      escola=escola,
                      quantidades_periodo=quantidades_periodo)
