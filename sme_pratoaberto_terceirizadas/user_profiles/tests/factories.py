import factory
import random

from .. import models
from ...users.tests.factories import UserFactory

ABBREVIATIONS = ['BT', 'CL', 'CS', 'FB', 'FO', 'G', 'IP',
                 'IQ', 'JT', 'MP', 'PE', 'PJ', 'SA', 'SM']


def generate_cpf_mask(cpf):
    cpf = cpf[:3] + "." + cpf[3:6] + "." + cpf[6:9] + "-" + cpf[9:]
    return cpf


def generate_cnpj_mask(cnpj):
    cnpj = cnpj[:2] + "." + cnpj[2:5] + "." + cnpj[5:8] + "/" + cnpj[8:12] + "-" + cnpj[12:14]
    return cnpj


class BaseAbstractPersonIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True
        model = models.BaseAbstractPersonIndividual

    cpf = generate_cpf_mask(str(random.randint(10000000000, 99999999999)))


class BaseAbstractPersonCompanyFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True
        model = models.BaseAbstractPersonCompany

    cnpj = generate_cnpj_mask(str(random.randint(10000000000000, 99999999999999)))
    state_registry = factory.Faker('random_number', digits=20)


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
