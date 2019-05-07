import pytest

from .meal_kit.tests.factories import MealKitFactory
from .permission.tests.factories import PermissionFactory, ProfilePermissionFactory
from .users.tests.factories import ProfileFactory


@pytest.fixture
def sample():
    return 'teste'


@pytest.fixture
def meal_kit() -> MealKitFactory:
    return MealKitFactory()


@pytest.fixture
def profile() -> ProfileFactory:
    return ProfileFactory()


@pytest.fixture
def permission() -> PermissionFactory:
    return PermissionFactory()


@pytest.fixture
def profile_permission() -> ProfilePermissionFactory:
    return ProfilePermissionFactory()
