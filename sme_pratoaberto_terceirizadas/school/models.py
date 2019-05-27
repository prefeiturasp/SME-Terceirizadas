from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, Activable, TemChaveExterna
from sme_pratoaberto_terceirizadas.users.models import User


class RegionalDirector(Describable):
    """DRE - Diretoria Regional"""
    # TODO chave estrangeira para Institution
    abbreviation = models.CharField(_('Abbreviation'), max_length=10)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return _('Abbreviation') + self.abbreviation

    class Meta:
        verbose_name = _("Regional Director")
        verbose_name_plural = _("Regional Directors")


class SchoolPeriod(Describable):
    """Períodos Escolares"""
    FIRST_PERIOD = 'first_period'
    SECOND_PERIOD = 'second_period'
    THIRD_PERIOD = 'third_period'
    FOURTH_PERIOD = 'fourth_period'
    INTEGRATE = 'integrate'
    value = models.CharField(max_length=50, blank=True, null=True)
    meal_types = models.ManyToManyField('food.MealType', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School Period")
        verbose_name_plural = _("School Periods")


class SchoolAge(Describable, Activable, TemChaveExterna):
    """Tabela utilizada para registrar faixa etária de idade"""


class Borough(Describable, Activable):
    """Sub Prefeitura"""


class SchoolUnitType(Describable, Activable):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""


class ManagementType(Describable, Activable):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""


class SchoolGroup(TemChaveExterna):
    """Agrupamento"""
    codigo = models.SmallIntegerField(_('Grouping'))


class School(Describable, Activable):
    """Escola"""
    # TODO chave estrangeira para Institution
    name = models.CharField(_("Name"), max_length=160)
    eol_code = models.CharField(_("EOL code"), max_length=10)
    codae_code = models.CharField(_('CODAE code'), max_length=10)
    grouping = models.ForeignKey(SchoolGroup,
                                 on_delete=models.DO_NOTHING,
                                 blank=True,
                                 null=True)
    regional_director = models.ForeignKey(RegionalDirector,
                                          on_delete=models.DO_NOTHING,
                                          blank=True,
                                          null=True)
    unit_type = models.ForeignKey(SchoolUnitType,
                                  on_delete=models.DO_NOTHING,
                                  blank=True,
                                  null=True)
    management_type = models.ForeignKey(ManagementType,
                                        on_delete=models.DO_NOTHING,
                                        blank=True,
                                        null=True)
    borough = models.ForeignKey(Borough,
                                blank=True,
                                null=True,
                                on_delete=models.DO_NOTHING)
    ages = models.ManyToManyField(SchoolAge, blank=True)
    periods = models.ManyToManyField(SchoolPeriod, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
