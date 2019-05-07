import pytest

pytestmark = pytest.mark.django_db


def test_meal_kit_name(meal_kit):
    assert meal_kit.name == 'Jessica Bradley'


def test_meal_kit_description(meal_kit):
    assert meal_kit.description == 'Hit reveal rise now. Her medical enjoy city point nice.'
