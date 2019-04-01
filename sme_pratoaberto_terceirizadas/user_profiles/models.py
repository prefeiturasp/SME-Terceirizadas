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


class Describable(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"), max_length=256)

    class Meta:
        abstract = True


class Activable(models.Model):
    is_active = models.BooleanField(_("Active"))

    class Meta:
        abstract = True


class OutSourcedProfile(User, BaseAbstractPersonCompany):
    """Terceirizada"""
    # colocar campos de edital


class SubManagerProfile(User, BaseAbstractPersonIndividual):
    """Cogestor"""


class AlternateProfile(User, BaseAbstractPersonIndividual):
    """Suplente"""


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


#
# Endereço
#

class CityLocation(models.Model):
    """TODO: deixar pre cadastrada cidade São Paulo e UF PA"""
    city = models.CharField(_("City"), max_length=50)
    state = models.CharField(_("UF"), max_length=2)


class Address(models.Model):
    """TODO: usar futuramente https://viacep.com.br/ para preencher automaticamente endereço"""
    street_name = models.CharField(_("Street name"), max_length=256)
    complement = models.CharField(_("Complement"), max_length=30)
    district = models.CharField(_("District"), max_length=30)
    number = models.CharField(_("Number"), max_length=6)
    postal_code = models.CharField(_("Postal code"), max_length=9)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    city_location = models.ForeignKey(CityLocation,
                                      on_delete=models.DO_NOTHING,
                                      null=True)


#
# Relacionados a escolas
#


class SubTownHall(Describable, Activable):
    """Sub Prefeitura"""


class SchoolUnitType(Describable, Activable):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""


class ManagementType(Describable, Activable):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""


class SchoolProfile(User, Describable, Activable):
    """Escola"""
    eol_code = models.CharField(_("EOL code"), max_length=6)
    codae_code = models.CharField(_('CODAE code'), max_length=6)
    grouping = models.SmallIntegerField(_('Grouping'))

    # fks
    regional_director = models.ForeignKey(RegionalDirectorProfile,
                                          on_delete=models.DO_NOTHING,
                                          null=True)
    address = models.ForeignKey(Address,
                                on_delete=models.DO_NOTHING,
                                null=True)
    unit_type = models.ForeignKey(SchoolUnitType,
                                  on_delete=models.DO_NOTHING,
                                  null=True)
    management_type = models.ForeignKey(ManagementType,
                                        on_delete=models.DO_NOTHING,
                                        null=True)
    sub_town_hall = models.ForeignKey(SubTownHall,
                                      on_delete=models.DO_NOTHING,
                                      null=True)

    def __str__(self):
        return _('School') + self.name

#
# TODO: criar apps separados?
#
