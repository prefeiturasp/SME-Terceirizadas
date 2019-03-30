from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    is_nutritionist = models.BooleanField(default=False, editable=False)
    is_regional_director = models.BooleanField(default=False, editable=False)
    is_alternate = models.BooleanField(default=False, editable=False)
    is_sub_manager = models.BooleanField(default=False, editable=False)
    is_outsourced = models.BooleanField(default=False, editable=False)
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
