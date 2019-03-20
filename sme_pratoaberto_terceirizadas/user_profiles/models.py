from enum import Enum

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseAbstractPersonIndividual(models.Model):
    cpf = models.CharField(_('CPF'), max_length=11, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class BaseAbstractPersonCompany(models.Model):
    cnpj = models.CharField(_('CNPJ'), max_length=11, unique=True, blank=True, null=True)
    state_registry = models.CharField(_('State Registry'), max_length=11, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class BasePerson(models.Model):
    class STATUSES(Enum):
        active = ('act', 'Active')
        inactive = ('ina', 'Inactive')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    name = models.CharField(_('Functional register'), max_length=256)
    email = models.EmailField(_('E-mail'), max_length=60, unique=True, blank=True, null=True)
    functional_register = models.CharField(_('Functional register'), max_length=60, unique=True, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    status = models.CharField(max_length=3,
                              choices=[x.value for x in STATUSES],
                              default=STATUSES.active.value[0])


class OutSourcedProfile(BasePerson, BaseAbstractPersonCompany):
    """Terceirizada"""
    # colocar campos de edital


class SubManagerProfile(BasePerson, BaseAbstractPersonIndividual):
    """Cogestor"""


class AlternateProfile(BasePerson, BaseAbstractPersonIndividual):
    """Suplente"""
    pass


class RegionalDirectorProfile(models.Model):
    """DRE - Diretoria Regional"""
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)
    description = models.TextField(_('Description'), max_length=256)
    sub_manager = models.ForeignKey(SubManagerProfile, on_delete=models.DO_NOTHING, null=True)
    alternate = models.ForeignKey(AlternateProfile, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return 'Abbreviation: {}'.format(self.abbreviation)


class NutritionistProfile(BasePerson, BaseAbstractPersonIndividual):
    """Nutri"""
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return 'Nutritionist: {}'.format(self.name)
