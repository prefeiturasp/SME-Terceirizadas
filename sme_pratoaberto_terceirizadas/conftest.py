import pytest

from sme_pratoaberto_terceirizadas.meal_kit.tests.factories import MealKitFactory
from sme_pratoaberto_terceirizadas.permission.tests.factories import PermissionFactory, ProfilePermissionFactory


@pytest.fixture
def sample():
    return 'teste'


@pytest.fixture
def meal_kit() -> MealKitFactory:
    return MealKitFactory()


@pytest.fixture
def profile_permission() -> ProfilePermissionFactory:
    return ProfilePermissionFactory()


@pytest.fixture
def permission() -> PermissionFactory:
    return PermissionFactory()
