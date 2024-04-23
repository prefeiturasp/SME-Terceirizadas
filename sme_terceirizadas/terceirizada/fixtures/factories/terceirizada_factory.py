from factory import DjangoModelFactory, LazyFunction, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.terceirizada.models import Contrato, Edital, Terceirizada

fake = Faker("pt_BR")


class EmpresaFactory(DjangoModelFactory):
    class Meta:
        model = Terceirizada

    nome_fantasia = Sequence(lambda n: f"Empresa {fake.unique.name()}")
    razao_social = Sequence(lambda n: f"Empresa {fake.unique.name()} LTDA")
    cnpj = Sequence(
        lambda n: fake.unique.cnpj().replace(".", "").replace("/", "").replace("-", "")
    )


class EditalFactory(DjangoModelFactory):
    class Meta:
        model = Edital

    numero = Sequence(lambda n: fake.unique.random_int(min=1, max=1000))
    objeto = Sequence(lambda n: f"objeto {fake.unique.name()}")


class ContratoFactory(DjangoModelFactory):
    class Meta:
        model = Contrato

    numero = Sequence(lambda _: f"{fake.unique.random_int(min=1, max=1000)}")
    terceirizada = SubFactory(EmpresaFactory)
    edital = SubFactory(EditalFactory)
    ata = LazyFunction(lambda: str(fake.random_number(digits=10, fix_len=True)))
    numero_chamada_publica = LazyFunction(
        lambda: str(fake.random_number(digits=10, fix_len=True))
    )
