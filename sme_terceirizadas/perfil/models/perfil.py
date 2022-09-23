import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django_prometheus.models import ExportModelOperationsMixin

from ...dados_comuns.behaviors import Ativavel, Descritivel, Nomeavel, TemChaveExterna
from ...dados_comuns.tasks import envia_email_unico_task


class Perfil(ExportModelOperationsMixin('perfil'), Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes."""

    # Visão Choices
    ESCOLA = 'ESCOLA'
    DRE = 'DRE'
    CODAE = 'CODAE'
    EMPRESA = 'EMPRESA'

    VISAO_CHOICES = (
        (ESCOLA, 'Escola'),
        (DRE, 'Diretoria Regional'),
        (CODAE, 'Codae'),
        (EMPRESA, 'Empresa'),
    )

    super_usuario = models.BooleanField('Super usuario na instiuição?', default=False)
    visao = models.CharField( # noqa
        'Visão', choices=VISAO_CHOICES, max_length=25, blank=True, null=True, default=None)

    @classmethod
    def visoes_to_json(cls):
        result = []
        for visao in cls.VISAO_CHOICES:
            choice = {
                'id': visao[0],
                'nome': visao[1]
            }
            result.append(choice)
        return result

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome


class Vinculo(ExportModelOperationsMixin('vinculo_perfil'), Ativavel, TemChaveExterna):
    """Para informar que tipo de funcao uma pessoa teve em um dado intervalo de tempo em uma instituição.

    Ex.: de jan a dez de 2018 (Intervalo) Ciclano (Usuário) foi Diretor (Perfil) na instituição ESCOLA (instituicao)
    """

    (STATUS_AGUARDANDO_ATIVACAO,
     STATUS_ATIVO,
     STATUS_FINALIZADO) = range(3)

    data_inicial = models.DateField('Data inicial', null=True, blank=True)
    data_final = models.DateField('Data final', null=True, blank=True)
    perfil = models.ForeignKey('Perfil', on_delete=models.PROTECT)
    usuario = models.ForeignKey('Usuario', on_delete=models.PROTECT, related_name='vinculos')

    limit = (models.Q(app_label='escola', model='escola') |  # noqa W504
             models.Q(app_label='escola', model='diretoriaregional') |  # noqa W504
             models.Q(app_label='escola', model='codae') |  # noqa W504
             models.Q(app_label='terceirizada', model='terceirizada'))

    # https://docs.djangoproject.com/en/2.2/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True,
                                     limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    instituicao = GenericForeignKey('content_type', 'object_id')

    @property
    def status(self):
        if (not self.data_inicial) and (not self.data_final) and self.ativo is False:
            status = self.STATUS_AGUARDANDO_ATIVACAO
        elif self.data_inicial and self.ativo and not self.data_final:
            status = self.STATUS_ATIVO
        elif self.data_inicial and self.data_final and self.ativo is False:
            status = self.STATUS_FINALIZADO
        else:
            raise IntegrityError('Status invalido')
        return status

    def finalizar_vinculo(self):
        self.usuario.is_active = False
        self.usuario.save()
        self.ativo = False
        self.data_final = datetime.date.today()
        self.save()
        titulo = 'Vínculo finalizado'
        conteudo = 'Seu vínculo com o SIGPAE foi finalizado por seu superior.'
        template = 'email_conteudo_simples.html'
        dados_template = {'titulo': titulo, 'conteudo': conteudo}
        html = render_to_string(template, dados_template)
        envia_email_unico_task.delay(
            assunto='Vínculo finalizado - SIGPAE',
            corpo='',
            email=self.usuario.email,
            template=template,
            dados_template=dados_template,
            html=html
        )

    def ativar_vinculo(self):
        self.ativo = True
        self.data_inicial = datetime.date.today()
        self.save()

    class Meta:
        verbose_name = 'Vínculo'
        verbose_name_plural = 'Vínculos'

    def __str__(self):
        return f'{self.usuario} de {self.data_inicial} até {self.data_final}'
