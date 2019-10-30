import environ
import requests
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

from ...dados_comuns.behaviors import TemChaveExterna
from ...dados_comuns.utils import url_configs

env = environ.Env()


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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # type: ignore

    @property
    def vinculos(self):
        return self.vinculos

    @property
    def vinculo_atual(self):
        if self.vinculos.filter(ativo=True).exists():
            return self.vinculos.get(ativo=True)
        return None

    @property
    def tipo_usuario(self):
        tipo_usuario = 'indefinido'
        if self.vinculos.filter(ativo=True).exists():
            tipo_usuario = self.vinculos.get(ativo=True).tipo_instituicao.model
            if tipo_usuario == 'diretoriaregional':
                return 'diretoria_regional'
        return tipo_usuario

    @property
    def pode_efetuar_cadastro(self):
        headers = {'Authorization': f'Token {env("DJANGO_EOL_API_TOKEN")}'}
        r = requests.get(f'{env("DJANGO_EOL_API_URL")}/cargos/{self.registro_funcional}', headers=headers)
        response = r.json()
        pode_efetuar_cadastro = False
        for result in response['results']:
            if result['cargo'] == 'DIRETOR DE ESCOLA':
                pode_efetuar_cadastro = True
                break
        return pode_efetuar_cadastro

    # TODO: verificar o from_email
    def enviar_email_confirmacao(self):
        self.add_email_if_not_exists(self.email)
        content = {'uuid': self.uuid, 'confirmation_key': self.confirmation_key}
        url_configs('CONFIRMAR_EMAIL', content)
        self.email_user(
            subject='Confirme seu e-mail - SIGPAE',
            message=f'Clique neste link para confirmar seu e-mail no SIGPAE \n'
            f': {url_configs("CONFIRMAR_EMAIL", content)}',
        )
