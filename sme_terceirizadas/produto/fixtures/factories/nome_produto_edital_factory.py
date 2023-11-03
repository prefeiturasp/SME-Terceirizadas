from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.produto.models import NomeDeProdutoEdital

fake = Faker('pt_BR')


class NomeDeProdutoEditalFactory(DjangoModelFactory):
    class Meta:
        model = NomeDeProdutoEdital

    nome = Sequence(lambda n: f'{fake.unique.name()}')
