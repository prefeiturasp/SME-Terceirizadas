import pytest
from faker import Faker
from model_mommy import mommy

from sme_pratoaberto_terceirizadas.alimento.models import Refeicao
from sme_pratoaberto_terceirizadas.meal_kit.models import SolicitacaoKitLanche
from .meal_kit.models import KitLanche
from .permission.models import Permissao, PermissaoPerfil
from .users.models import Perfil, Instituicao

fake = Faker('pt_BR')
fake.seed(420)


# README -> https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures

@pytest.fixture
def meal_kit():
    meals = mommy.make(Refeicao, _quantity=4)
    return mommy.make(KitLanche, nome='kit lance nro tal',
                      descricao='este kit lanche foi feito por fulano em...',
                      refeicoes=meals)


@pytest.fixture(scope="function", params=[('4h','6h', '8h'])
def order_meal_kit(request):
    param = request.param
    refeicoes = mommy.make(Refeicao, _quantity=4)
    kit_lanches = mommy.make(KitLanche, nome='kit lance nro tal',
                           descricao='este kit lanche foi feito por fulano em...',
                           refeicoes=refeicoes, _quantity=5)
    return mommy.make(SolicitacaoKitLanche, localizacao='rua dos bobos numero 9', tempo_agendado=param, kit_lanches=kit_lanches)


@pytest.fixture
def profile():
    institution = mommy.make(Instituicao, name='Faker SA')
    return mommy.make(Perfil, title='título do perfil', institution=institution)


@pytest.fixture
def permission():
    return mommy.make(Permissao, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')


@pytest.fixture
def profile_permission():
    permission = mommy.make(Permissao, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')
    return mommy.make(PermissaoPerfil, permission=permission)
