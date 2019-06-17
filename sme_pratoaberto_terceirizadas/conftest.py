import pytest
from faker import Faker
from model_mommy import mommy

from sme_pratoaberto_terceirizadas.alimento.models import Refeicao
from sme_pratoaberto_terceirizadas.meal_kit.models import OrderMealKit
from .meal_kit.models import MealKit
from .permission.models import Permission, ProfilePermission
from .users.models import Profile, Institution

fake = Faker('pt_BR')
fake.seed(420)


# README -> https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures

@pytest.fixture
def meal_kit():
    meals = mommy.make(Refeicao, _quantity=4)
    return mommy.make(MealKit, name='kit lance nro tal',
                      description='este kit lanche foi feito por fulano em...',
                      meals=meals)


@pytest.fixture(scope="function", params=['4h', '6h', '8h'])
def order_meal_kit(request):
    param = request.param
    meals = mommy.make(Refeicao, _quantity=4)
    meal_kits = mommy.make(MealKit, name='kit lance nro tal',
                           description='este kit lanche foi feito por fulano em...',
                           meals=meals, _quantity=5)
    return mommy.make(OrderMealKit, location='rua dos bobos numero 9', scheduled_time=param, meal_kits=meal_kits)


@pytest.fixture
def profile():
    institution = mommy.make(Institution, name='Faker SA')
    return mommy.make(Profile, title='título do perfil', institution=institution)


@pytest.fixture
def permission():
    return mommy.make(Permission, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')


@pytest.fixture
def profile_permission():
    permission = mommy.make(Permission, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')
    return mommy.make(ProfilePermission, permission=permission)
