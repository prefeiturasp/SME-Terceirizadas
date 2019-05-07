import pytest

from sme_pratoaberto_terceirizadas.meal_kit.tests.factories import MealKitFactory


@pytest.fixture
def sample():
    return 'teste'


@pytest.fixture
def meal_kit() -> MealKitFactory:
    return MealKitFactory()
