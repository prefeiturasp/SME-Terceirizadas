from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable


class MealKit(Describable):
    """Kit Lanche"""

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Meal Kit")
        verbose_name_plural = _("Meal Kits")
