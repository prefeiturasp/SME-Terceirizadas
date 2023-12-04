from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.produto.models import Fabricante, Marca, NomeDeProdutoEdital

fake = Faker("pt_BR")


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


class FabricanteFactory(DjangoModelFactory):
    class Meta:
        model = Fabricante

    nome = Sequence(lambda n: str(fake.unique.name()).upper())


class MarcaFactory(DjangoModelFactory):
    class Meta:
        model = Marca

    nome = Sequence(lambda n: str(fake.unique.name()).upper())
