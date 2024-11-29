import factory
from factory import (
    DjangoModelFactory,
    LazyAttribute,
    LazyFunction,
    Sequence,
    SubFactory,
)
from faker import Faker

from sme_terceirizadas.terceirizada.models import Contrato, Edital, Terceirizada

fake = Faker("pt_BR")


class EmpresaFactory(DjangoModelFactory):
    class Meta:
        model = Terceirizada

    nome_fantasia = Sequence(lambda n: f"Empresa {n}")
    razao_social = LazyAttribute(lambda obj: f"{obj.nome_fantasia} LTDA")
    cnpj = Sequence(
        lambda n: fake.unique.cnpj().replace(".", "").replace("/", "").replace("-", "")
    )


class EditalFactory(DjangoModelFactory):
    class Meta:
        model = Edital

    numero = Sequence(lambda n: f"{str(n).zfill(5)}")
    objeto = Sequence(lambda n: f"Objeto {n}")


class ContratoFactory(DjangoModelFactory):
    numero = Sequence(lambda n: f"{str(n).zfill(5)}")
    terceirizada = SubFactory(EmpresaFactory)
    edital = SubFactory(EditalFactory)
    ata = LazyFunction(lambda: str(fake.random_number(digits=10, fix_len=True)))
    numero_chamada_publica = LazyFunction(
        lambda: str(fake.random_number(digits=10, fix_len=True))
    )

    @factory.post_generation
    def lotes(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for lote in extracted:
                self.lotes.add(lote)

    class Meta:
        model = Contrato
