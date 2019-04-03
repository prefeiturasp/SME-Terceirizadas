import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    functional_register = models.CharField(_('Functional register'), max_length=60,
                                           unique=True, blank=True, null=True)
    objects = BaseUserManager()
