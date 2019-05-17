import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable
from sme_pratoaberto_terceirizadas.food.models import Meal
from sme_pratoaberto_terceirizadas.school.models import School


class MealKit(models.Model):
    """Kit Lanche"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_('Name'), max_length=160)
    description = models.TextField(_('Description'), blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    meals = models.ManyToManyField(Meal)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Meal Kit")
        verbose_name_plural = _("Meal Kits")


class OrderMealKit(models.Model):
    """ Solicitação de kit lanche """

    TYPES_STATUS = (('SAVED', 'SALVO'), ('SENDED', 'ENVIADO'))
    location = models.CharField(_('Order Location'), max_length=160)
    students_quantity = models.IntegerField(_('Students Quantity'))
    order_date = models.DateField(_('Order Date'))
    schools = models.ManyToManyField(School)
    meal_kits = models.ManyToManyField(MealKit)
    observation = models.TextField(_('Observation'), blank=True, null=True)
    status = models.CharField(_('Status'), choices=TYPES_STATUS, default=0, max_length=6)
