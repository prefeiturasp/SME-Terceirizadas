from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, Activable
from sme_pratoaberto_terceirizadas.common_data.models import Address


class RegionalDirector(Describable):
    """DRE - Diretoria Regional"""
    abbreviation = models.CharField(_('Abbreviation'), max_length=4)

    # TODO: resolve imports
    # alternate = models.ForeignKey('AlternateProfile', verbose_name=_('Alternate'),
    #                               on_delete=models.DO_NOTHING, null=True)
    # sub_manager = models.ForeignKey('SubManagerProfile',
    #                                 verbose_name=_('Sub Manager'),
    #                                 on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return _('Abbreviation') + self.abbreviation

    class Meta:
        verbose_name = _("Regional Director")
        verbose_name_plural = _("Regional Directors")


class Borough(Describable, Activable):
    """Sub Prefeitura"""


class SchoolUnitType(Describable, Activable):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""


class ManagementType(Describable, Activable):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""


class School(Describable, Activable):
    """Escola"""
    eol_code = models.CharField(_("EOL code"), max_length=6)
    codae_code = models.CharField(_('CODAE code'), max_length=6)
    grouping = models.SmallIntegerField(_('Grouping'))

    # fks
    regional_director = models.ForeignKey(RegionalDirector,
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
    borough = models.ForeignKey(Borough,
                                on_delete=models.DO_NOTHING,
                                null=True)

    def __str__(self):
        return _('School') + self.name
