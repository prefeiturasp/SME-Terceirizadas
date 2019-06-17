import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, RegistroHora
from sme_pratoaberto_terceirizadas.escola.models import IdadeEscolar, GrupoEscolar, TipoUnidadeEscolar, TipoGestao
from sme_pratoaberto_terceirizadas.users.models import User

now = timezone.now()


class MenuStatus(models.Model):
    """Status do Cardápio"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_("Title"), max_length=99)


class MenuType(Descritivel):
    """Tipo de Menu (Comum, Lactante, Diabético, etc)"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Food(models.Model):
    """Alimento"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_("Title"), max_length=99)
    details = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class MealType(Descritivel):
    """Tipo de Refeição"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Meal Type")
        verbose_name_plural = _("Meal Types")


class Meal(models.Model):
    """Refeição """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_("title"), max_length=50)
    description = models.TextField(_("Description"), blank=True, null=True, max_length=256)
    foods = models.ManyToManyField(Food)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Meal")
        verbose_name_plural = _("Meals")


class DayMenu(RegistroHora):
    """Cardápio para um dia"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.ForeignKey(MenuStatus, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    management = models.ForeignKey(TipoGestao, on_delete=models.DO_NOTHING)
    unit_type = models.ForeignKey(TipoUnidadeEscolar, on_delete=models.DO_NOTHING)
    grouping = models.ForeignKey(GrupoEscolar, on_delete=models.DO_NOTHING)
    date = models.DateField()
    age = models.ForeignKey(IdadeEscolar, on_delete=models.DO_NOTHING)
    meals = models.ManyToManyField(Meal)
