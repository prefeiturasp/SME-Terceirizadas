from django.db import models
from django.utils.translation import ugettext_lazy as _


class Describable(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"), max_length=256)

    class Meta:
        abstract = True


class Activable(models.Model):
    is_active = models.BooleanField(_("Active"))

    class Meta:
        abstract = True


class TimestampAble(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
