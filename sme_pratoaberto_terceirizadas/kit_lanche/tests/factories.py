from factory import DjangoModelFactory, Faker, random

from ..models import KitLanche

random.reseed_random('seed')


class MealKitFactory(DjangoModelFactory):
    description = Faker("paragraph")
    name = Faker("name")

    class Meta:
        model = KitLanche
        django_get_or_create = ["name"]


class MealsFactory(DjangoModelFactory):
    uuid = Faker('ean13')
    meal_title = Faker('job')
