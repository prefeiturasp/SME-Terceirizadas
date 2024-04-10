from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.imr.models import TipoGravidade, TipoPenalidade
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import (
    EditalFactory,
)

fake = Faker("pt_BR")


class TipoGravidadeFactory(DjangoModelFactory):
    class Meta:
        model = TipoGravidade

    tipo = Sequence(lambda n: f"tipo - {fake.unique.name()}")


class TipoPenalidadeFactory(DjangoModelFactory):
    class Meta:
        model = TipoPenalidade

    edital = SubFactory(EditalFactory)
    numero_clausula = Sequence(lambda n: fake.unique.random_int(min=1, max=1000))
    descricao = Sequence(lambda n: f"descrição - {fake.unique.name()}")
    gravidade = SubFactory(TipoGravidadeFactory)
