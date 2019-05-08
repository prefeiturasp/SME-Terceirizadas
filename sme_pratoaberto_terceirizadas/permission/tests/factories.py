from factory import DjangoModelFactory, Faker, random, SubFactory, post_generation, Sequence

from sme_pratoaberto_terceirizadas.users.tests.factories import ProfileFactory
from ..models import Permission, ProfilePermission

random.reseed_random('seed')


class PermissionFactory(DjangoModelFactory):
    uuid = Faker("md5")
    title = Faker("job")
    endpoint = Faker("url")
    id = Sequence(lambda n: n)

    @post_generation
    def permissions(self, create, extracted, **kwargs):
        print(create, extracted, kwargs, 'awsiodasdjsaidjiosa')
        if extracted:
            # A list of groups were passed in, use them
            for permission in extracted:
                self.permissions.add(permission)

    class Meta:
        model = Permission
        django_get_or_create = ["title"]


class ProfilePermissionFactory(DjangoModelFactory):
    permission = SubFactory(PermissionFactory)
    profile = SubFactory(ProfileFactory)
    verbs = 'R'

    class Meta:
        model = ProfilePermission
        django_get_or_create = ["verbs"]
