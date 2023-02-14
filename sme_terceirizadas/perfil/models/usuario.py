import datetime
import logging

import environ
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

from ...dados_comuns.behaviors import ArquivoCargaBase, Ativavel, Nomeavel, TemChaveExterna
from ...dados_comuns.constants import (
    ADMINISTRADOR_CODAE_DILOG_CONTABIL,
    ADMINISTRADOR_CODAE_DILOG_JURIDICO,
    ADMINISTRADOR_CODAE_GABINETE,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    ADMINISTRADOR_GESTAO_PRODUTO,
    ADMINISTRADOR_MEDICAO,
    ADMINISTRADOR_SUPERVISAO_NUTRICAO,
    COORDENADOR_CODAE_DILOG_LOGISTICA,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    COORDENADOR_GESTAO_PRODUTO,
    COORDENADOR_LOGISTICA,
    COORDENADOR_SUPERVISAO_NUTRICAO,
    COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
    DILOG_CRONOGRAMA,
    DILOG_DIRETORIA,
    DILOG_QUALIDADE,
    DINUTRE_DIRETORIA
)
from ...dados_comuns.tasks import envia_email_unico_task
from ...dados_comuns.utils import url_configs
from ...eol_servico.utils import EOLService
from ..models import Perfil, Vinculo

log = logging.getLogger('sigpae.usuario')

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
        help_text=_('Designates whether the user can log into this admin site.'),  # noqa
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

    def email_user(self, subject, message, from_email=None, template=None, dados_template=None, html=None, **kwargs):
        """Send an email to this user."""
        envia_email_unico_task.delay(assunto=subject, corpo='', email=self.email, template=template,
                                     dados_template=dados_template, html=html)


# TODO: Refatorar classe Usuário para comportar classes Pessoa, Usuário,
# Nutricionista
class Usuario(ExportModelOperationsMixin('usuario'), SimpleEmailConfirmationUserMixin, CustomAbstractUser,
              TemChaveExterna):
    """Classe de autenticacao do django, ela tem muitos perfis."""

    SME = 0
    PREFEITURA = 1

    TIPOS_EMAIL = (
        (SME, '@sme.prefeitura.sp.gov.br'),
        (PREFEITURA, '@prefeitura.sp.gov.br')
    )
    nome = models.CharField(_('name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    tipo_email = models.PositiveSmallIntegerField(choices=TIPOS_EMAIL,
                                                  null=True, blank=True)

    registro_funcional = models.CharField(_('RF'), max_length=7, blank=True, null=True, unique=True,  # noqa DJ01
                                          validators=[MinLengthValidator(7)])
    cargo = models.CharField(max_length=50, blank=True)

    # TODO: essew atributow deve pertencer somente a um model Pessoa
    cpf = models.CharField(_('CPF'), max_length=11, blank=True, null=True, unique=True,  # noqa DJ01
                           validators=[MinLengthValidator(11)])
    contatos = models.ManyToManyField('dados_comuns.Contato', blank=True)

    # TODO: esses atributos devem pertencer somente a um model Nutricionista
    super_admin_terceirizadas = models.BooleanField('É Administrador por parte das Terceirizadas?',
                                                    default=False)  # noqa
    crn_numero = models.CharField('Nutricionista crn', max_length=160, blank=True, null=True)  # noqa DJ01

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # type: ignore

    def atualizar_cargo(self):
        cargo = self.cargos.filter(ativo=True).last()
        self.cargo = cargo.nome
        self.save()

    def desativa_cargo(self):
        cargo = self.cargos.last()
        if cargo is not None:
            cargo.finalizar_cargo()

    @property
    def vinculos(self):
        return self.vinculos

    @property
    def vinculo_atual(self):
        if self.vinculos.filter(Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
                                Q(data_inicial__isnull=False, data_final=None, ativo=True)).exists():
            return self.vinculos.get(
                Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
                Q(data_inicial__isnull=False, data_final=None, ativo=True))
        return None

    @property
    def tipo_usuario(self):  # noqa C901
        tipo_usuario = 'indefinido'
        if self.vinculo_atual:
            tipo_usuario = self.vinculo_atual.content_type.model
            if tipo_usuario == 'codae':
                if self.vinculo_atual.perfil.nome in [COORDENADOR_LOGISTICA, COORDENADOR_CODAE_DILOG_LOGISTICA,
                                                      ADMINISTRADOR_CODAE_GABINETE, ADMINISTRADOR_CODAE_DILOG_JURIDICO,
                                                      ADMINISTRADOR_CODAE_DILOG_CONTABIL]:
                    tipo_usuario = 'logistica_abastecimento'
                elif self.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                        ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]:
                    tipo_usuario = 'gestao_alimentacao_terceirizada'
                elif self.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_PRODUTO,
                                                        ADMINISTRADOR_GESTAO_PRODUTO]:
                    tipo_usuario = 'gestao_produto'
                elif self.vinculo_atual.perfil.nome in [COORDENADOR_SUPERVISAO_NUTRICAO,
                                                        ADMINISTRADOR_SUPERVISAO_NUTRICAO]:
                    tipo_usuario = 'supervisao_nutricao'
                elif self.vinculo_atual.perfil.nome in [COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO]:
                    tipo_usuario = 'nutricao_manifestacao'
                elif self.vinculo_atual.perfil.nome in [ADMINISTRADOR_MEDICAO]:
                    tipo_usuario = 'medicao'
                elif self.vinculo_atual.perfil.nome in [DILOG_CRONOGRAMA, DILOG_QUALIDADE, DILOG_DIRETORIA,
                                                        DINUTRE_DIRETORIA]:
                    tipo_usuario = 'pre_recebimento'
                else:
                    tipo_usuario = 'dieta_especial'
        return tipo_usuario

    @property
    def pode_efetuar_cadastro(self):
        dados_usuario = EOLService.get_informacoes_usuario(self.registro_funcional)  # noqa
        diretor_de_escola = False
        for dado in dados_usuario:
            if dado['cargo'] == 'DIRETOR DE ESCOLA':
                diretor_de_escola = True
                break
        vinculo_aguardando_ativacao = self.vinculo_atual.status == Vinculo.STATUS_AGUARDANDO_ATIVACAO
        return diretor_de_escola or vinculo_aguardando_ativacao

    def enviar_email_confirmacao(self):
        self.add_email_if_not_exists(self.email)
        content = {'uuid': self.uuid,
                   'confirmation_key': self.confirmation_key}
        titulo = 'Confirmação de E-mail'
        template = 'email_cadastro_funcionario.html'
        dados_template = {
            'titulo': titulo,
            'link_cadastro': url_configs('CONFIRMAR_EMAIL', content),
            'nome': self.nome
        }
        html = render_to_string(template, dados_template)
        self.email_user(
            subject='Confirme seu e-mail - SIGPAE',
            message='',
            template=template,
            dados_template=dados_template,
            html=html,

        )

    def enviar_email_recuperacao_senha(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self)
        content = {'uuid': self.uuid, 'confirmation_key': token}
        titulo = 'Recuperação de senha'
        conteudo = f'Clique neste link para criar uma nova senha no SIGPAE: {url_configs("RECUPERAR_SENHA", content)}'
        template = 'email_conteudo_simples.html'
        dados_template = {'titulo': titulo, 'conteudo': conteudo}
        html = render_to_string(template, dados_template)
        self.email_user(
            subject='Email de recuperação de senha - SIGPAE',
            message='',
            template=template,
            dados_template=dados_template,
            html=html,
        )

    def enviar_email_administrador(self):
        self.add_email_if_not_exists(self.email)
        titulo = '[SIGPAE] Novo cadastro de empresa'
        template = 'email_cadastro_terceirizada.html'
        dados_template = {'titulo': titulo, 'link_cadastro': url_configs(
            'LOGIN_TERCEIRIZADAS', {}), 'nome': self.nome}
        html = render_to_string(template, dados_template)
        self.email_user(
            subject='[SIGPAE] Novo cadastro de empresa',
            message='',
            template=template,
            dados_template=dados_template,
            html=html
        )

    def atualiza_senha(self, senha, token):
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(self, token):
            self.set_password(senha)
            self.save()
            return True
        return False

    def criar_vinculo_administrador(self, instituicao, nome_perfil):
        perfil = Perfil.objects.get(nome=nome_perfil)
        Vinculo.objects.create(
            instituicao=instituicao,
            perfil=perfil,
            usuario=self,
            ativo=False
        )

    class Meta:
        ordering = ('-super_admin_terceirizadas',)


class Cargo(TemChaveExterna, Nomeavel, Ativavel):
    data_inicial = models.DateField('Data inicial', null=True, blank=True)
    data_final = models.DateField('Data final', null=True, blank=True)
    usuario = models.ForeignKey(
        Usuario,
        related_name='cargos',
        on_delete=models.CASCADE
    )

    def finalizar_cargo(self):
        self.ativo = False
        self.data_final = datetime.date.today()
        self.save()

    def ativar_cargo(self):
        self.ativo = True
        self.data_inicial = datetime.date.today()
        self.save()

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return f'{self.usuario} de {self.data_inicial} até {self.data_final}'


class PlanilhaDiretorCogestor(models.Model):  # noqa D204
    """
    Importa dados de planilha específica de Diretores e Cogestores.
    No momento apenas DRE Ipiranga.
    """

    arquivo = models.FileField(blank=True, null=True)  # noqa DJ01
    criado_em = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    def __str__(self):
        return str(self.arquivo)

    class Meta:
        ordering = ('-criado_em',)
        verbose_name = 'Planilha Diretor Cogestor'
        verbose_name_plural = 'Planilhas Diretores Cogestores'


class ImportacaoPlanilhaUsuarioPerfilEscola(ArquivoCargaBase):
    """Importa dados de planilha de usuários com perfil Escola."""

    resultado = models.FileField(blank=True, default='')

    class Meta:
        verbose_name = 'Arquivo para importação de usuário perfil Escola'
        verbose_name_plural = 'Arquivos para importação de usuários perfil Escola'

    def __str__(self) -> str:
        return str(self.conteudo)


class ImportacaoPlanilhaUsuarioPerfilCodae(ArquivoCargaBase):
    """Importa dados de planilha de usuários com perfil Escola."""

    resultado = models.FileField(blank=True, default='')

    class Meta:
        verbose_name = 'Arquivo para importação de usuário perfil Codae'
        verbose_name_plural = 'Arquivos para importação de usuários perfil Codae'

    def __str__(self) -> str:
        return str(self.conteudo)


class ImportacaoPlanilhaUsuarioPerfilDre(ArquivoCargaBase):
    """Importa dados de planilha de usuários com perfil Dre."""

    resultado = models.FileField(blank=True, default='')

    class Meta:
        verbose_name = 'Arquivo para importação de usuário perfil Dre'
        verbose_name_plural = 'Arquivos para importação de usuários perfil Dre'

    def __str__(self) -> str:
        return str(self.conteudo)
