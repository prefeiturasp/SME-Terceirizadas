from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.produto.models import NomeDeProdutoEdital

fake = Faker('pt_BR')


class ProdutoLogisticaFactory(DjangoModelFactory):
    class Meta:
        model = NomeDeProdutoEdital

    nome = Sequence(lambda n: str(fake.unique.name()).upper())
    tipo_produto = NomeDeProdutoEdital.LOGISTICA


class ProdutoTerceirizadaFactory(DjangoModelFactory):
    class Meta:
        model = NomeDeProdutoEdital

    nome = Sequence(lambda n: str(fake.unique.name()).upper())
    tipo_produto = NomeDeProdutoEdital.TERCEIRIZADA
