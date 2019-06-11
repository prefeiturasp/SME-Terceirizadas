import pytest
from faker import Faker
from model_mommy import mommy

from sme_pratoaberto_terceirizadas.permission.models import Permission, ProfilePermission
from .meal_kit.tests.factories import MealKitFactory
from .users.tests.factories import ProfileFactory

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def meal_kit() -> MealKitFactory:
    return MealKitFactory()


@pytest.fixture
def profile() -> ProfileFactory:
    return ProfileFactory()


@pytest.fixture
def permission():
    return mommy.make(Permission, title=fake.sentence(), endpoint=fake.url())


@pytest.fixture
def profile_permission():
    permission = mommy.make(Permission, title=fake.sentence(), endpoint=fake.url())
    return mommy.make(ProfilePermission, permission=permission)
