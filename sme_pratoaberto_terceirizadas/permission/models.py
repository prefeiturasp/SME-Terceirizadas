import uuid as uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..users.models import Profile


class Permission(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('title'), max_length=90)
    endpoint = models.CharField(_('endpoint'), max_length=90)
    permissions = models.ManyToManyField(Profile, through='ProfilePermission',
                                         through_fields=('permission', 'profile'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')


class ProfilePermission(models.Model):
    """ Tabela intermediária entre Profile e Permission """

    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    permission = models.ForeignKey(Permission, on_delete=models.PROTECT)
    verbs = models.CharField(_('Verbs'), default='R', max_length=2,
                             help_text='Campo utilizado para indenticar o nível de permissão'
                                       ' do usuário (R : Read-only, W : Writer)')

    def __str__(self):
        return '{} - {}'.format(self.profile, self.permission)

    class Meta:
        verbose_name = _('Permission from Profile')
        verbose_name_plural = _('Permissions from Profile')
