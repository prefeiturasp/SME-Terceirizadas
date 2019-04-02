from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, Activable
from sme_pratoaberto_terceirizadas.school.models import RegionalDirector
from sme_pratoaberto_terceirizadas.users.models import User


class BaseAbstractPersonIndividual(models.Model):
    cpf = models.CharField(_('CPF'), max_length=15, unique=True, blank=True, null=True)
    functional_register = models.CharField(_('Functional register'), max_length=60, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class BaseAbstractPersonCompany(models.Model):
    cnpj = models.CharField(_('CNPJ'), max_length=18, unique=True, blank=True, null=True)
    state_registry = models.CharField(_('State Registry'), max_length=20, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class OutSourcedProfile(User, BaseAbstractPersonCompany):
    """Terceirizada"""
    # colocar campos de edital


class SubManagerProfile(User, BaseAbstractPersonIndividual):
    """Cogestor"""


class AlternateProfile(User, BaseAbstractPersonIndividual):
    """Suplente"""


class NutritionistProfile(User, BaseAbstractPersonIndividual):
    """Nutricionista"""
    regional_director = models.ForeignKey(RegionalDirector,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return _('Nutritionist') + self.first_name

    class Meta:
        verbose_name = _("Nutritionist")
