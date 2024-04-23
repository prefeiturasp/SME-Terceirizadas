from datetime import date, timedelta

from factory import DjangoModelFactory, LazyFunction, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.fixtures.factories.cronograma_factory import (
    EtapasDoCronogramaFactory,
)
from sme_terceirizadas.recebimento.models import FichaDeRecebimento

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
