from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_sigpae_api.produto.models import (
    Fabricante,
    InformacaoNutricional,
    Marca,
    NomeDeProdutoEdital,
    TipoDeInformacaoNutricional,
)

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


class TipoDeInformacaoNutricionalFactory(DjangoModelFactory):
    class Meta:
        model = TipoDeInformacaoNutricional


class InformacaoNutricionalFactory(DjangoModelFactory):
    class Meta:
        model = InformacaoNutricional

    tipo_nutricional = SubFactory(TipoDeInformacaoNutricionalFactory)
