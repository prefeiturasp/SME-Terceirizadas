from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.models import Cronograma
from sme_terceirizadas.produto.fixtures.factories.nome_produto_edital_factory import NomeDeProdutoEditalFactory
from sme_terceirizadas.produto.models import NomeDeProdutoEdital
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import EmpresaFactory

fake = Faker('pt_BR')


class CronogramaFactory(DjangoModelFactory):
    class Meta:
        model = Cronograma

    numero = Sequence(lambda n: f'{str(fake.unique.random_int(min=0, max=1000))}/{str(fake.date(pattern="%Y"))}')
    empresa = SubFactory(EmpresaFactory)
    produto = SubFactory(NomeDeProdutoEditalFactory, tipo_produto=NomeDeProdutoEdital.LOGISTICA)
