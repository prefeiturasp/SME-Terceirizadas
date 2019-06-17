import uuid as uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, Ativavel, TemChaveExterna
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.terceirizada.models import Lote



class DiretoriaRegional(Descritivel):
    """DRE - Diretoria Regional"""
    # TODO chave estrangeira para Institution
    codigo = models.CharField(_('Codigo'), max_length=10)
    users = models.ManyToManyField(User, blank=True, related_name='DREs')

    def __str__(self):
        return _('Codigo') + self.codigo

    class Meta:
        verbose_name = _("Diretor Regional")
        verbose_name_plural = _("Diretores Regionais")


class IdadeEscolar(Descritivel, Ativavel, TemChaveExterna):
    """Tabela utilizada para registrar faixa etária de idade"""


class SubPrefeitura(Descritivel, Ativavel):
    """Sub Prefeitura"""


class TipoUnidadeEscolar(Descritivel, Ativavel):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""


class TipoGestao(Descritivel, Ativavel):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""


class GrupoEscolar(TemChaveExterna):
    """Agrupamento"""
    codigo = models.SmallIntegerField(_('Grouping'))

    class Meta:
        verbose_name = _("Grupo Escolar")
        verbose_name_plural = _("Grupos Escolares")


class PeriodoEscolar(Descritivel):
    """Períodos Escolares"""
    PRIMEIRO_PERIODO = 'primeiro_periodo'
    SEGUNDO_PERIODO = 'segundo_periodo'
    TERCEIRO_PERIODO = 'terceiro_periodo'
    QUARTO_PERIODO = 'quarto_periodo'
    INTEGRAL = 'integral'
    valor = models.CharField(max_length=50, blank=True, null=True)
    tipo_refeicao = models.ManyToManyField('alimento.TipoRefeicao', blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Periodo Escolar")
        verbose_name_plural = _("Periodos Escolares")


class Escola(Ativavel):
    """Escola"""
    # TODO chave estrangeira para Institution
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(_("Nome"), max_length=160)
    codigo_eol = models.CharField(_("Codigo EOL"), max_length=10)
    codigo_codae = models.CharField(_('Codigo CODAE'), max_length=10)
    lote = models.ForeignKey(Lote,
                             on_delete=models.DO_NOTHING,
                             blank=True,
                             null=True)
    agrupamento = models.ForeignKey(GrupoEscolar,
                                    on_delete=models.DO_NOTHING,
                                    blank=True,
                                    null=True)
    diretoria_regional = models.ForeignKey(DiretoriaRegional,
                                           on_delete=models.DO_NOTHING,
                                           blank=True,
                                           null=True)
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar,
                                     on_delete=models.DO_NOTHING,
                                     blank=True,
                                     null=True)
    tipo_gestao = models.ForeignKey(TipoGestao,
                                    on_delete=models.DO_NOTHING,
                                    blank=True,
                                    null=True)
    sub_prefeitura = models.ForeignKey(SubPrefeitura,
                                       blank=True,
                                       null=True,
                                       on_delete=models.DO_NOTHING)
    idades = models.ManyToManyField(IdadeEscolar, blank=True)
    periodos = models.ManyToManyField(PeriodoEscolar, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.nome
