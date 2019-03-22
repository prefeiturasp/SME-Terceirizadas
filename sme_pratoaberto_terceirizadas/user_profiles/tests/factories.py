import factory

from .. import models
from ...users.tests.factories import UserFactory


ABBREVIATIONS = ['BT', 'CL', 'CS', 'FB', 'FO', 'G', 'IP',
                 'IQ', 'JT', 'MP', 'PE', 'PJ', 'SA', 'SM']


class BaseAbstractPersonIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True
        model = models.BaseAbstractPersonIndividual

    cpf = factory.Faker('random_number', digits=11)


class BaseAbstractPersonCompanyFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True
        model = models.BaseAbstractPersonCompany


class OutSourceProfileFactory(UserFactory, BaseAbstractPersonCompanyFactory):
    class Meta:
        model = models.OutSourcedProfile


class AlternateProfileFactory(UserFactory, BaseAbstractPersonIndividualFactory):
    class Meta:
        model = models.AlternateProfile


class SubManagerProfileFactory(UserFactory, BaseAbstractPersonIndividualFactory):
    class Meta:
        model = models.SubManagerProfile


class RegionalDirectorProfileFactory(factory.Factory):
    class Meta:
        model = models.RegionalDirectorProfile

    abbreviation = factory.Faker('word', ext_word_list=ABBREVIATIONS)
    alternate = factory.SubFactory(AlternateProfileFactory)
    description = factory.Faker('sentence')
    sub_manager = factory.SubFactory(SubManagerProfileFactory)


class NutritionistProfileFactory(UserFactory, BaseAbstractPersonIndividualFactory):
    class Meta:
        model = models.NutritionistProfile

    regional_director = factory.SubFactory(RegionalDirectorProfileFactory)
