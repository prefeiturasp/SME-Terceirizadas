from django.core.validators import MinLengthValidator
from django.db import models

from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from ..dados_comuns.models_abstract import (Ativavel, Iniciais, Nomeavel, TemChaveExterna)


class DiretoriaRegional(Nomeavel, TemChaveExterna):
    usuarios = models.ManyToManyField(Usuario)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Diretoria regional"
        verbose_name_plural = "Diretorias regionais"


class FaixaIdadeEscolar(Nomeavel, Ativavel, TemChaveExterna):
    """
        Ex. de 1 a 2 anos
        de 2 a 5 anos
        de 7 a 18 anos.
        de 6 meses a 1 ano
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Idade escolar"
        verbose_name_plural = "Idades escolares"


class TipoUnidadeEscolar(Iniciais, Ativavel, TemChaveExterna):
    """
        Tipo de unidade escolar: EEMEF, CIEJA, EMEI, EMEBS, CEI, CEMEI...
    """

    def __str__(self):
        return self.iniciais

    class Meta:
        verbose_name = "Tipo de unidade escolar"
        verbose_name_plural = "Tipos de unidade escolar"


class TipoGestao(Nomeavel, Ativavel, TemChaveExterna):
    """
        Ex.: Terceirizada completa, tec mista
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de gestão"
        verbose_name_plural = "Tipos de gestão"


class PeriodoEscolar(Nomeavel, TemChaveExterna):
    """
        manhã, intermediário, tarde, vespertino, noturno, integral
    """

    class Meta:
        verbose_name = "Período escolar"
        verbose_name_plural = "Períodos escolares"

    def __str__(self):
        return self.nome


class Escola(Ativavel, TemChaveExterna):
    nome = models.CharField("Nome", max_length=160, blank=True, null=True)
    codigo_eol = models.CharField("Código EOL", max_length=6, unique=True, validators=[MinLengthValidator(6)])
    codigo_codae = models.CharField('Código CODAE', max_length=10, unique=True,
                                    blank=True, null=True)
    quantidade_alunos = models.PositiveSmallIntegerField("Quantidade de alunos")

    diretoria_regional = models.ForeignKey(DiretoriaRegional,
                                           related_name='escolas',
                                           on_delete=models.DO_NOTHING)
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar,
                                     on_delete=models.DO_NOTHING)
    tipo_gestao = models.ForeignKey(TipoGestao,
                                    on_delete=models.DO_NOTHING)
    lote = models.ForeignKey('terceirizada.Lote',
                             on_delete=models.DO_NOTHING)

    endereco = models.ForeignKey('dados_comuns.Endereco', on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    contato = models.ForeignKey('dados_comuns.Contato', on_delete=models.DO_NOTHING,
                                blank=True, null=True)

    idades = models.ManyToManyField(FaixaIdadeEscolar, blank=True)
    periodos_escolares = models.ManyToManyField(PeriodoEscolar, blank=True)
    cardapios = models.ManyToManyField('cardapio.Cardapio', blank=True)
    usuarios = models.ManyToManyField(Usuario)

    def get_grupos_inclusao_normal(self):
        return self.grupos_inclusoes_normais

    def get_inclusoes_alimentacao_continua(self):
        return self.inclusoes_alimentacao_continua

    def __str__(self):
        return '{}: {}'.format(self.codigo_eol, self.nome)

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
