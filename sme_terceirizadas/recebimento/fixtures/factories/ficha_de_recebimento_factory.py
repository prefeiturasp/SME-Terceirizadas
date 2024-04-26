from datetime import date, timedelta

from factory import DjangoModelFactory, LazyFunction, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.fixtures.factories.cronograma_factory import (
    EtapasDoCronogramaFactory,
)
from sme_terceirizadas.recebimento.models import (
    FichaDeRecebimento,
    VeiculoFichaDeRecebimento,
)

fake = Faker("pt_BR")


class FichaDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = FichaDeRecebimento

    etapa = SubFactory(EtapasDoCronogramaFactory)
    data_entrega = LazyFunction(
        lambda: fake.date_time_between(
            start_date=date.today() + timedelta(days=10)
        ).date()
    )


class VeiculoFichaDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = VeiculoFichaDeRecebimento

    ficha_recebimento = SubFactory(FichaDeRecebimentoFactory)
    numero = Sequence(lambda n: f"Veículo {n}")
