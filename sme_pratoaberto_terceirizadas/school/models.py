from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, Activable
from sme_pratoaberto_terceirizadas.common_data.models import Address


class RegionalDirector(Describable):
    """DRE - Diretoria Regional"""
    # TODO chave estrangeira para Institution
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)

    def __str__(self):
        return _('Abbreviation') + self.abbreviation

    class Meta:
        verbose_name = _("Regional Director")
        verbose_name_plural = _("Regional Directors")


class SchoolAge(Describable, Activable):
    """Tabela utilizada para registrar faiza etária de idade"""


class Borough(Describable, Activable):
    """Sub Prefeitura"""


class SchoolUnitType(Describable, Activable):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""


class ManagementType(Describable, Activable):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""


class School(Describable, Activable):
    """Escola"""
    # TODO chave estrangeira para Institution
    eol_code = models.CharField(_("EOL code"), max_length=6)
    codae_code = models.CharField(_('CODAE code'), max_length=6)
    grouping = models.SmallIntegerField(_('Grouping'))

    # fks
    regional_director = models.ForeignKey(RegionalDirector,
                                          on_delete=models.DO_NOTHING,
                                          null=True)
    unit_type = models.ForeignKey(SchoolUnitType,
                                  on_delete=models.DO_NOTHING,
                                  null=True)
    management_type = models.ForeignKey(ManagementType,
                                        on_delete=models.DO_NOTHING,
                                        null=True)
    borough = models.ForeignKey(Borough,
                                on_delete=models.DO_NOTHING,
                                null=True)
    ages = models.ManyToManyField(SchoolAge,
                                  on_delete=models.DO_NOTHING,
                                  null=True)

    def __str__(self):
        return _('School') + self.name
