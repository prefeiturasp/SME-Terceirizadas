import uuid as uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..users.models import Perfil, Instituicao


class Permissao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(_('titulo'), max_length=90)
    endpoint = models.CharField(_('endpoint'), max_length=90)
    permissoes = models.ManyToManyField(Perfil, through='PerfilPermissao',
                                        through_fields=('permissao', 'perfil'))
    instituicao = models.ForeignKey(Instituicao, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = _('Permissao')
        verbose_name_plural = _('Permissoes')


class PerfilPermissao(models.Model):
    """ Tabela intermediária entre Profile e Permission """

    perfil = models.ForeignKey(Perfil, on_delete=models.PROTECT)
    permissao = models.ForeignKey(Permissao, on_delete=models.PROTECT)
    acao = models.CharField(_('Acao'), default='R', max_length=2,
                            help_text='Campo utilizado para indenticar o nível de permissão'
                                       ' do usuário (R : Read-only (Apenas-Leitura), W : Writer (Escrita) )')

    def __str__(self):
        return '{} - {}'.format(self.perfil, self.permissao)

    class Meta:
        verbose_name = _('Permissao do Perfil')
        verbose_name_plural = _('Permissoes do Perfil')
