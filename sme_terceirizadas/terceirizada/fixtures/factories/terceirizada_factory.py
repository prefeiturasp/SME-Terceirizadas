from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.terceirizada.models import Edital, Terceirizada

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
