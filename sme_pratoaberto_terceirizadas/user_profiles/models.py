from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.users.models import User


class BaseAbstractPersonIndividual(models.Model):
    cpf = models.CharField(_('CPF'), max_length=11, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class BaseAbstractPersonCompany(models.Model):
    cnpj = models.CharField(_('CNPJ'), max_length=11, unique=True, blank=True, null=True)
    state_registry = models.CharField(_('State Registry'), max_length=11, unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class OutSourcedProfile(User, BaseAbstractPersonCompany):
    """Terceirizada"""
    # colocar campos de edital


class SubManagerProfile(User, BaseAbstractPersonIndividual):
    """Cogestor"""


class AlternateProfile(User, BaseAbstractPersonIndividual):
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


class NutritionistProfile(User, BaseAbstractPersonIndividual):
    """Nutri"""
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return 'Nutritionist: {}'.format(self.first_name)
