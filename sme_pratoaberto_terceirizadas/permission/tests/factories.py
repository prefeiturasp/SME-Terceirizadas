from factory import DjangoModelFactory, Faker, random, SubFactory

from ..models import Permission, ProfilePermission

random.reseed_random('seed')


class PermissionFactory(DjangoModelFactory):
    uuid = Faker("md5")
    title = Faker("name")
    endpoint = Faker("url")

    class Meta:
        model = Permission
        django_get_or_create = ["title"]


class ProfilePermissionFactory(DjangoModelFactory):
    permission = SubFactory(PermissionFactory)
    profile = 1
    verbs = 'R'

    class Meta:
        model = ProfilePermission
        django_get_or_create = ["verbs"]
