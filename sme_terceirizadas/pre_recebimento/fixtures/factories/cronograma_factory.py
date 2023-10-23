from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.pre_recebimento.models import Cronograma

fake = Faker('pt_BR')


class CronogramaFactory(DjangoModelFactory):
    class Meta:
        model = Cronograma

    numero = Sequence(lambda n: f'{str(fake.unique.random_int(min=0, max=1000))}/{str(fake.date(pattern="%Y"))}')
