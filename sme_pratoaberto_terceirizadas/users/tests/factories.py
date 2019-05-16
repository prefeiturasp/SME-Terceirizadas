from factory import DjangoModelFactory, Faker, random, SubFactory

from ..models import Profile, Institution

random.reseed_random('seed')


class InstitutionFactory(DjangoModelFactory):
    uuid = Faker('md5')
    name = Faker('paragraph', nb_sentences=1, variable_nb_sentences=True, ext_word_list=None)

    class Meta:
        model = Institution
        django_get_or_create = ["name"]


class ProfileFactory(DjangoModelFactory):
    uuid = Faker("md5")
    title = Faker("name")
    is_active = True
    institution = SubFactory(InstitutionFactory)

    class Meta:
        model = Profile
        django_get_or_create = ["title"]
