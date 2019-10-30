from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.utils import IntegrityError

from ...dados_comuns.behaviors import (
    Ativavel, Descritivel, Nomeavel, TemChaveExterna
)


class Perfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes."""

    super_usuario = models.BooleanField('Super usuario na instiuição?', default=False)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome


class Vinculo(Ativavel, TemChaveExterna):
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

    class Meta:
        verbose_name = 'Vínculo'
        verbose_name_plural = 'Vínculos'

    def __str__(self):
        return f'{self.usuario} de {self.data_inicial} até {self.data_final}'
