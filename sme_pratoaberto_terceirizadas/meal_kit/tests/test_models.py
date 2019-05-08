import pytest

pytestmark = pytest.mark.django_db


def test_meal_kit_attrs(meal_kit):
    assert meal_kit.name == 'Jessica Bradley'
    assert meal_kit.description == 'Door ten experience amount. Gas mind indeed notice live while analysis crime.'
    assert meal_kit.__str__() == 'Jessica Bradley'


def test_meal_kit_meta(meal_kit):
    assert meal_kit._meta.verbose_name_plural == "Meal Kits"
    assert meal_kit._meta.verbose_name == "Meal Kit"
