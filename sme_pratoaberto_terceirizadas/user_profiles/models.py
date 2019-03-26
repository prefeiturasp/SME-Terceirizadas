from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.users.models import User


class BaseAbstractPersonIndividual(models.Model):
    cpf = models.CharField(_('CPF'), max_length=15, unique=True, blank=True, null=True)

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
    pass


class RegionalDirectorProfile(models.Model):
    """DRE - Diretoria Regional"""
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)
    alternate = models.ForeignKey(AlternateProfile, verbose_name=_('Alternate'), on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(_('Description'), max_length=256)
    sub_manager = models.ForeignKey(SubManagerProfile,
                                    verbose_name=_('Sub Manager'),
                                    on_delete=models.DO_NOTHING,
                                    null=True)

    def __str__(self):
        return _('Abbreviation') + ': %s' % self.abbreviation

    class Meta:
        verbose_name = _("Regional Director")
        verbose_name_plural = _("Regional Directors")


class NutritionistProfile(User, BaseAbstractPersonIndividual):
    """Nutricionista"""
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return _('Nutritionist') + ': %s' % self.first_name

    class Meta:
        verbose_name = _("Nutritionist")
