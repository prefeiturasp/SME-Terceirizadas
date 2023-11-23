from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.models import Cronograma, Laboratorio, UnidadeMedida
from sme_terceirizadas.produto.fixtures.factories.produto_factory import ProdutoLogisticaFactory
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import EmpresaFactory

fake = Faker('pt_BR')


class CronogramaFactory(DjangoModelFactory):
    class Meta:
        model = Cronograma

    numero = Sequence(lambda n: f'{str(fake.unique.random_int(min=0, max=1000))}/{str(fake.date(pattern="%Y"))}')
    empresa = SubFactory(EmpresaFactory)
    produto = SubFactory(ProdutoLogisticaFactory)


class LaboratorioFactory(DjangoModelFactory):
    class Meta:
        model = Laboratorio

    nome = Sequence(lambda n: f'Laboratorio {fake.unique.name()}')
    cnpj = Sequence(lambda n: fake.unique.cnpj().replace('.', '').replace('/', '').replace('-', ''))


class UnidadeMedidaFactory(DjangoModelFactory):
    class Meta:
        model = UnidadeMedida

    abreviacao = Sequence(lambda n: fake.unique.pystr(min_chars=3, max_chars=3).upper())
    nome = Sequence(lambda n: f'Laboratorio {fake.unique.name()}')
