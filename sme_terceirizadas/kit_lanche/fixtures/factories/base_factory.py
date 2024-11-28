import factory
from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.kit_lanche.models import (
    KitLanche,
    SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa,
)
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import (
    EditalFactory,
)

fake = Faker("pt_BR")


class KitLancheFactory(DjangoModelFactory):
    edital = SubFactory(EditalFactory)
    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")

    @factory.post_generation
    def tipos_unidades(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tipo_unidade in extracted:
                self.tipos_unidades.add(tipo_unidade)

    class Meta:
        model = KitLanche


class SolicitacaoKitLancheFactory(DjangoModelFactory):
    tempo_passeio = Sequence(lambda n: fake.unique.random_int(min=0, max=2))

    @factory.post_generation
    def kits(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for kit in extracted:
                self.kits.add(kit)

    class Meta:
        model = SolicitacaoKitLanche


class SolicitacaoKitLancheAvulsaBaseFactory(DjangoModelFactory):
    solicitacao_kit_lanche = SubFactory(SolicitacaoKitLancheFactory)

    class Meta:
        model = SolicitacaoKitLancheAvulsa
