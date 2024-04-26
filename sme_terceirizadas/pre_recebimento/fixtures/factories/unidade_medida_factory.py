from factory import DjangoModelFactory, LazyAttribute, Sequence
from faker import Faker

from sme_terceirizadas.pre_recebimento.models import UnidadeMedida

fake = Faker("pt_BR")


class UnidadeMedidaFactory(DjangoModelFactory):
    class Meta:
        model = UnidadeMedida

    nome = Sequence(lambda n: f"Unidade {n}")
    abreviacao = LazyAttribute(lambda obj: obj.nome[:3])
