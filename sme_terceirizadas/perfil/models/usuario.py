from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

from .perfil import Perfil
from ...dados_comuns.models_abstract import TemChaveExterna


# Thanks to https://github.com/jmfederico/django-use-email-as-username


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    """An abstract base class implementing a fully featured User model with admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Usuario(SimpleEmailConfirmationUserMixin, CustomAbstractUser, TemChaveExterna):
    """Classe de autenticacao do django, ela tem muitos perfis."""

    nome = models.CharField(_('name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    cpf = models.CharField(_('CPF'), max_length=11, default='')
    registro_funcional = models.CharField(_('RF'), max_length=10, default='')
    perfis = models.ManyToManyField(Perfil)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # type: ignore

    @property
    def escolas(self):
        return self.escolas

    @property
    def diretorias_regionais(self):
        return self.diretorias_regionais

    @property  # noqa C901
    def tipo_usuario(self):
        if self.escolas.exists():
            return 'escola'
        elif self.diretorias_regionais.exists():
            return 'diretoria_regional'
        elif self.CODAE.exists():
            return 'codae'
        elif self.terceirizadas.exists():
            return 'terceirizada'
        else:
            return 'indefinido'
