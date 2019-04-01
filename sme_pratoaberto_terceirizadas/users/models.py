import uuid

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser,PermissionsMixin):
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_trusty = models.BooleanField(_('trusty'), default=False,
                                    help_text=_('Designates whether this user has confirmed his account.'))


    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

