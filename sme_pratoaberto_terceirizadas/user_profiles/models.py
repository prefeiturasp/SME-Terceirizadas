from enum import Enum

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseProfile(models.Model):
    """
    An abstract base class model that provides common data between profiles.
    """

    class STATUSES(Enum):
        active = ('act', 'Active')
        inactive = ('ina', 'Inactive')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    name = models.CharField(_('Functional register'), max_length=256)
    email = models.EmailField(_('E-mail'), max_length=60, unique=True)
    functional_register = models.CharField(_('Functional register'), max_length=60, unique=True)
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    status = models.CharField(max_length=3,
                              choices=[x.value for x in STATUSES],
                              default=STATUSES.active.value[0])

    class Meta:
        abstract = True


class OutSourcedProfile(BaseProfile):
    """Terceirizada"""
    pass


class SubManagerProfile(BaseProfile):
    """Cogestor"""
    pass


class AlternateProfile(BaseProfile):
    """Suplente"""
    pass


class RegionalDirectorProfile(BaseProfile):
    """DRE - Diretoria Regional"""
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)
    description = models.TextField(_('Description'), max_length=256)
    sub_manager = models.ForeignKey(SubManagerProfile, null=True, on_delete=models.DO_NOTHING)
    alternate = models.ForeignKey(AlternateProfile, null=True, on_delete=models.DO_NOTHING)


class NutritionistProfile(BaseProfile):
    """Nutri"""
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          null=True,
                                          on_delete=models.DO_NOTHING)
