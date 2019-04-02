import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    title = models.CharField(_('title'), max_length=90)
    is_active = models.BooleanField(_('is_active'), default=True)


class UserManager(BaseUserManager):
    pass


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_('name'), max_length=150)
    email = models.CharField(_('email'), unique=True)
    functional_register = models.CharField(_('functional register'),)
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_trusty = models.BooleanField(_('trusty'), default=False,
                                    help_text=_('Designates whether this user has confirmed his account.'))
    profile = models.ForeignKey(Profile, verbose_name=_('profile'), on_delete=models.DO_NOTHING)

    is_staff = models.BooleanField(_('is_staff'), default=False)
    is_active = models.BooleanField(_('is_active'), default=True)
    admin = models.BooleanField(_('admin'), default=False)

    def __str__(self):
        return self.name

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_staff(self):
        return self.is_staff

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', '']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email])

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
