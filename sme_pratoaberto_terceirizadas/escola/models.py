from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Sum

from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from ..dados_comuns.models_abstract import (Ativavel, Iniciais, Nomeavel, TemChaveExterna)


class DiretoriaRegional(Nomeavel, TemChaveExterna):
    usuarios = models.ManyToManyField(Usuario, related_name='diretorias_regionais', blank=True)

    @property
    def escolas(self):
        return self.escolas

    @property
    def quantidade_alunos(self):
        return DiretoriaRegional.objects.annotate(
            total_alunos=Sum('escolas__quantidade_alunos')).get(
            id=self.id).total_alunos

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
    cardapios = models.ManyToManyField('cardapio.Cardapio', blank=True,
                                       related_name='tipos_unidade_escolar')

    def get_cardapio(self, data):
        # TODO: ter certeza que tem so um cardapio por dia por tipo de u.e.
        try:
            return self.cardapios.get(data=data)
        except ObjectDoesNotExist:
            return None

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

    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao', related_name='periodos_escolares')

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
    lote = models.ForeignKey('Lote',
                             related_name='escolas',
                             on_delete=models.CASCADE)

    endereco = models.ForeignKey('dados_comuns.Endereco', on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    contato = models.ForeignKey('dados_comuns.Contato', on_delete=models.DO_NOTHING,
                                blank=True, null=True)

    idades = models.ManyToManyField(FaixaIdadeEscolar, blank=True)
    periodos_escolares = models.ManyToManyField(PeriodoEscolar, blank=True)
    usuarios = models.ManyToManyField(Usuario, related_name='escolas')

    @property
    def usuarios_diretoria_regional(self):
        return self.diretoria_regional.usuarios.all() if self.diretoria_regional else Usuario.objects.none()

    @property
    def grupos_inclusoes(self):
        return self.grupos_inclusoes_normais

    def get_cardapio(self, data):
        return self.tipo_unidade.get_cardapio(data)

    @property
    def inclusoes_continuas(self):
        return self.inclusoes_alimentacao_continua

    def __str__(self):
        return '{}: {}'.format(self.codigo_eol, self.nome)

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"


class Lote(TemChaveExterna, Nomeavel, Iniciais):
    """Lote de escolas"""
    tipo_gestao = models.ForeignKey(TipoGestao,
                                    on_delete=models.DO_NOTHING,
                                    related_name='lotes',
                                    null=True,
                                    blank=True)
    diretoria_regional = models.ForeignKey('escola.DiretoriaRegional',
                                           on_delete=models.DO_NOTHING,
                                           related_name='lotes',
                                           null=True,
                                           blank=True)
    terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                     on_delete=models.DO_NOTHING,
                                     related_name='lotes',
                                     null=True,
                                     blank=True)

    @property
    def escolas(self):
        return self.escolas

    def __str__(self):
        return self.nome + ' - ' + self.diretoria_regional.nome

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"


class Subprefeitura(Nomeavel, TemChaveExterna):
    diretoria_regional = models.ManyToManyField(DiretoriaRegional,
                                                related_name='subprefeituras',
                                                blank=True)
    lote = models.ForeignKey('Lote',
                             related_name='subprefeituras',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Subprefeitura"
        verbose_name_plural = "Subprefeituras"
