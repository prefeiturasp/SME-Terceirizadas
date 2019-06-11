import pytest

pytestmark = pytest.mark.django_db


def test_meal_kit_attrs(meal_kit):
    assert meal_kit.name == 'kit lance nro tal'
    assert meal_kit.description == 'este kit lanche foi feito por fulano em...'
    assert meal_kit.__str__() == 'kit lance nro tal'
    assert meal_kit.meals.count() == 3


def test_meal_kit_meta(meal_kit):
    assert meal_kit._meta.verbose_name_plural == "Meal Kits"
    assert meal_kit._meta.verbose_name == "Meal Kit"
