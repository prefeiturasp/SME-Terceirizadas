from django.db import models

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, Ativavel, TemChaveExterna, Iniciais, Nomeavel
from sme_pratoaberto_terceirizadas.terceirizada.models import Lote
from sme_pratoaberto_terceirizadas.perfil.models import Usuario


class DiretoriaRegional(Iniciais, Nomeavel):

    def __str__(self):
        return '{} : {}'.format(self.iniciais, self.nome)

    class Meta:
        verbose_name = "Diretoria regional"
        verbose_name_plural = "Diretorias regionais"


class IdadeEscolar(Nomeavel, Ativavel):
    """Tabela utilizada para registrar faixa etária de idade.
    3 a 5 anos, 3 a 11 meses, 12 meses a 18 meses, etc."""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Idade escolar"
        verbose_name_plural = "Idades escolares"


class SubPrefeitura(Ativavel):
    """Sub Prefeitura"""
    nome = models.CharField("Nome", max_length=160)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Sub prefeitura"
        verbose_name_plural = "Sub prefeituras"


class TipoUnidadeEscolar(Nomeavel, Ativavel):
    """Tipo de unidade escolar: EMEI, EMEF, CIEJA..."""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de unidade escolar"
        verbose_name_plural = "Tipos de unidade escolar"


class TipoGestao(Nomeavel, Ativavel):
    """Tipo de gestão escolar: DIRETA, MISTA, TERCEIRIZADA..."""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de gestão"
        verbose_name_plural = "Tipos de gestão"


class PeriodoEscolar(Nomeavel, Ativavel):
    """Períodos Escolares, manhã, tarde, noite, integral, intermediario, etc."""
    tipo_refeicao = models.ManyToManyField('alimento.TipoRefeicao', blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Período Escolar"
        verbose_name_plural = "Períodos Escolares"


class Escola(Ativavel, TemChaveExterna):
    nome = models.CharField("Nome", max_length=160, blank=True, null=True)
    codigo_eol = models.CharField("Codigo EOL", max_length=6)
    codigo_codae = models.CharField('Codigo CODAE', max_length=10)
    quantidade_alunos = models.PositiveSmallIntegerField("Quantidade de alunos")

    lote = models.ForeignKey(Lote,
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

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
