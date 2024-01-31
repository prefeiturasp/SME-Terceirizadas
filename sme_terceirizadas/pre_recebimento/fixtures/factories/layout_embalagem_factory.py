from factory import DjangoModelFactory, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.fixtures.factories.cronograma_factory import (
    CronogramaFactory,
)
from sme_terceirizadas.pre_recebimento.models import LayoutDeEmbalagem

fake = Faker("pt_BR")


class LayoutDeEmbalagemFactory(DjangoModelFactory):
    class Meta:
        model = LayoutDeEmbalagem

    cronograma = SubFactory(CronogramaFactory)
