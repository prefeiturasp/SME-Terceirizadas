from factory import DjangoModelFactory, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.models.cronograma import FichaTecnicaDoProduto
from sme_terceirizadas.produto.fixtures.factories.produto_factory import (
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
