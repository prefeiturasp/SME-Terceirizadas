from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.terceirizada.models import Terceirizada

fake = Faker('pt_BR')


class EmpresaFactory(DjangoModelFactory):
    class Meta:
        model = Terceirizada

    nome_fantasia = Sequence(lambda n: f'Empresa {fake.unique.name()}')
    razao_social = Sequence(lambda n: f'Empresa {fake.unique.name()} LTDA')
    cnpj = Sequence(lambda n: fake.unique.cnpj().replace('.', '').replace('/', '').replace('-', ''))
