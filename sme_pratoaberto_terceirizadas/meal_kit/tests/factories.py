from factory import DjangoModelFactory, Faker, random

from ..models import MealKit

random.reseed_random('seed')


class MealKitFactory(DjangoModelFactory):
    description = Faker("paragraph")
    name = Faker("name")

    class Meta:
        model = MealKit
        django_get_or_create = ["name"]


class MealsFactory(DjangoModelFactory):
    uuid = Faker('ean13')
    meal_title = Faker('job')
