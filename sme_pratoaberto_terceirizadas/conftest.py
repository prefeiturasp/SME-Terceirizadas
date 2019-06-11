import pytest
from faker import Faker
from model_mommy import mommy

from sme_pratoaberto_terceirizadas.food.models import Meal
from .meal_kit.models import MealKit
from .permission.models import Permission, ProfilePermission
from .users.models import Profile, Institution

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def meal_kit():
    meal1 = mommy.make(Meal)
    meal2 = mommy.make(Meal)
    meal3 = mommy.make(Meal)
    return mommy.make(MealKit, name='kit lance nro tal',
                      description='este kit lanche foi feito por fulano em...',
                      meals=[meal1, meal2, meal3])


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
