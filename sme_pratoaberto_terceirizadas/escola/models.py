from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, Ativavel, TemChaveExterna, Iniciais
from sme_pratoaberto_terceirizadas.terceirizada.models import Lote
from sme_pratoaberto_terceirizadas.users.models import User


class DiretoriaRegional(Iniciais, Descritivel):
    # TODO chave estrangeira para Institution
    users = models.ManyToManyField(User, blank=True, related_name='DREs')

    def __str__(self):
        return 'DRE: {}:'.format(self.iniciais)

    class Meta:
        verbose_name = _("Diretoria regional")
        verbose_name_plural = _("Diretorias regionais")


class IdadeEscolar(Descritivel, Ativavel):
    """Tabela utilizada para registrar faixa etária de idade.
    3 a 5 anos, 3 a 11 meses, 12 meses a 18 meses, etc."""

    def __str__(self):
        return self.nome


class SubPrefeitura(Descritivel, Ativavel):
    """Sub Prefeitura"""
    nome = models.CharField("Nome", max_length=160)

    def __str__(self):
        return self.nome


class TipoUnidadeEscolar(Descritivel, Ativavel):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""

    def __str__(self):
        return self.nome


class TipoGestao(Descritivel, Ativavel):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""

    def __str__(self):
        return self.nome


class PeriodoEscolar(Descritivel, Ativavel):
    """Períodos Escolares, manhã, tarde, noite, integral, intermediario, etc."""
    tipo_refeicao = models.ManyToManyField('alimento.TipoRefeicao', blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Período Escolar"
        verbose_name_plural = _("Períodos Escolares")


class Escola(Ativavel, TemChaveExterna):
    nome = models.CharField("Nome", max_length=160)
    codigo_eol = models.CharField("Codigo EOL", max_length=6)
    codigo_codae = models.CharField('Codigo CODAE', max_length=10)
    quantidade_alunos = models.PositiveSmallIntegerField("Quantidade de alunos")
    # lote = models.ForeignKey(Lote,
    #                          on_delete=models.DO_NOTHING,
    #                          blank=True,
    #                          null=True)
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

    idades = models.ManyToManyField(IdadeEscolar, blank=True, null=True)
    periodos = models.ManyToManyField(PeriodoEscolar, blank=True)

    # users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.nome
