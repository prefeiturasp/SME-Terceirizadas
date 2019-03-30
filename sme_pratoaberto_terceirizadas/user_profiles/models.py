from django.db import models
from django.utils.translation import ugettext_lazy as _

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
    # TODO: tem RF?
    """Terceirizada"""
    # colocar campos de edital


class SubManagerProfile(User, BaseAbstractPersonIndividual):
    """Cogestor"""


class AlternateProfile(User, BaseAbstractPersonIndividual):
    """Suplente"""
    pass


class RegionalDirectorProfile(User):
    """DRE - Diretoria Regional"""
    # TODO: na planilha de listas de unidades e empresas tem o nome das DRES. Adicionar aqui
    # TODO: planilhas de cogestores e da planilha  citada acima divergem nas siglas.
    # TODO: tem RF?
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)
    alternate = models.ForeignKey(AlternateProfile, verbose_name=_('Alternate'),
                                  on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(_('Description'), max_length=256)
    sub_manager = models.ForeignKey(SubManagerProfile,
                                    verbose_name=_('Sub Manager'),
                                    on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return _('Abbreviation') + self.abbreviation

    class Meta:
        verbose_name = _("Regional Director")
        verbose_name_plural = _("Regional Directors")


class NutritionistProfile(User, BaseAbstractPersonIndividual):
    """Nutricionista"""
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return _('Nutritionist') + self.first_name

    class Meta:
        verbose_name = _("Nutritionist")


class SchoolProfile(User):
    """Escola"""
    # TODO: consultar o weslei para mais detalhes.
    # TODO: tem RF?
    eol_code = models.CharField(_("EOL code"), max_length=6)
    codae_code = models.CharField(_('CODAE code'), max_length=6)
    # unity_scholar_type = models.ForeignKey emei emef...
    school_name = models.CharField(_("School name"), max_length=200)
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)

    def __str__(self):
        return _('School') + self.school_name
