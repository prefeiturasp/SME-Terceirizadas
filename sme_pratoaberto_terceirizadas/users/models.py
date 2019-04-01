import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        if not username:
            raise ValueError(_('The given username must be set'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_trusty = models.BooleanField(_('trusty'), default=False,
                                    help_text=_('Designates whether this user has confirmed his account.'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        managed = False
        db_table = 'user'

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email])

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
