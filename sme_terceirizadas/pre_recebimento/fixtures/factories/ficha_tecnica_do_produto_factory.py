from factory import DjangoModelFactory, LazyFunction, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.models.cronograma import (
    AnaliseFichaTecnica,
    FichaTecnicaDoProduto,
)
from sme_terceirizadas.produto.fixtures.factories.produto_factory import (
    MarcaFactory,
    ProdutoLogisticaFactory,
)
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import (
    EmpresaFactory,
)

fake = Faker("pt_BR")


class FichaTecnicaFactory(DjangoModelFactory):
    class Meta:
        model = FichaTecnicaDoProduto

    empresa = SubFactory(EmpresaFactory)
    produto = SubFactory(ProdutoLogisticaFactory)
    marca = SubFactory(MarcaFactory)
    peso_liquido_embalagem_primaria = LazyFunction(
        lambda: fake.random_number(digits=5, fix_len=True) / 100
    )
    peso_liquido_embalagem_secundaria = LazyFunction(
        lambda: fake.random_number(digits=5, fix_len=True) / 100
    )
    embalagem_primaria = LazyFunction(lambda: fake.text())
    embalagem_secundaria = LazyFunction(lambda: fake.text())


class AnaliseFichaTecnicaFactory(DjangoModelFactory):
    class Meta:
        model = AnaliseFichaTecnica

    ficha_tecnica = SubFactory(FichaTecnicaFactory)
