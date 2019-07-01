import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, CriadoEm, Nomeavel
from sme_pratoaberto_terceirizadas.escola.models import IdadeEscolar, TipoUnidadeEscolar, TipoGestao
from sme_pratoaberto_terceirizadas.perfil.models import Usuario

now = timezone.now()


class StatusCardapio(models.Model):
    """Status do Cardápio"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(_("Titulo"), max_length=99)


class TipoCardapio(Descritivel):
    """Tipo de Menu (Comum, Lactante, Diabético, etc)"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Alimento(models.Model):
    """Alimento"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(_("Titulo"), max_length=99)
    detalhes = models.TextField(_('Descricao'), blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo


class TipoRefeicao(Descritivel, Nomeavel):
    """Tipo de Refeição"""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Tipo de Refeição")
        verbose_name_plural = _("Tipos de refeições")


class Refeicao(models.Model):
    """Refeição """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(_("Titulo"), max_length=50)
    descricao = models.TextField(_("Descricao"), blank=True, null=True, max_length=256)
    alimentos = models.ManyToManyField(Alimento)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = _("Refeição")
        verbose_name_plural = _("Refeições")


class CardapioDia(CriadoEm):
    """Cardápio para um dia"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.ForeignKey(StatusCardapio, on_delete=models.DO_NOTHING)
    criado_por = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    tipo_gestao = models.ForeignKey(TipoGestao, on_delete=models.DO_NOTHING)
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar, on_delete=models.DO_NOTHING)
    data = models.DateField()
    idade = models.ForeignKey(IdadeEscolar, on_delete=models.DO_NOTHING)
    refeicoes = models.ManyToManyField(Refeicao)
