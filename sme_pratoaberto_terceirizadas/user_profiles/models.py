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
    email = models.EmailField(_('E-mail'))
    functional_register = models.IntegerField(_('Functional register'))
    status = models.CharField(max_length=3,
                              choices=[x.value for x in STATUSES])

    class Meta:
        abstract = True


class OutSourcedProfile(BaseProfile):
    """Terceirizada"""
    pass


class RegionalDirectorProfile(BaseProfile):
    """DRE"""
    pass


class NutritionistProfile(BaseProfile):
    """Nutri"""
    pass
    # regional_director = models.ForeignKey(DRE)
