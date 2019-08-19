from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Sum

from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import (
    InclusaoAlimentacaoContinua, GrupoInclusaoAlimentacaoNormal
)
from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from ..dados_comuns.models_abstract import (Ativavel, Iniciais, Nomeavel, TemChaveExterna)


class DiretoriaRegional(Nomeavel, TemChaveExterna):
    usuarios = models.ManyToManyField(Usuario, related_name='diretorias_regionais', blank=True)

    @property
    def escolas(self):
        return self.escolas

    @property
    def quantidade_alunos(self):
        quantidade_result = self.escolas.aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum', 0)

    @property
    def inclusoes_continuas_aprovadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_APROVADO
        )

    @property
    def inclusoes_normais_aprovadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            escola__in=self.escolas.all(),
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_APROVADO
        )

    @property
    def inclusoes_continuas_reprovadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_CANCELA_PEDIDO_ESCOLA
        )

    @property
    def inclusoes_normais_reprovadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            escola__in=self.escolas.all(),
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_CANCELA_PEDIDO_ESCOLA
        )

    # TODO: talvez fazer um manager genérico pra fazer esse filtro

    def inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(self, filtro_aplicado):
        if filtro_aplicado == "hoje":
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_vencendo_hoje
        else:
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_vencendo
        return inclusoes_continuas.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def inclusoes_continuas_das_minhas_escolas_no_prazo_limite(self, filtro_aplicado):
        if filtro_aplicado == "daqui_a_7_dias":
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_limite_daqui_a_7_dias
        else:
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_limite
        return inclusoes_continuas.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def inclusoes_continuas_das_minhas_escolas_no_prazo_regular(self, filtro_aplicado):
        if filtro_aplicado == "daqui_a_30_dias":
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_regular_daqui_a_30_dias
        elif filtro_aplicado == "daqui_a_7_dias":
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_regular_daqui_a_7_dias
        else:
            inclusoes_continuas = InclusaoAlimentacaoContinua.prazo_regular
        return inclusoes_continuas.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def inclusoes_normais_das_minhas_escolas_no_prazo_vencendo(self, filtro_aplicado):
        if filtro_aplicado == "hoje":
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_vencendo_hoje
        else:
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_vencendo
        return inclusoes_normais.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def inclusoes_normais_das_minhas_escolas_no_prazo_limite(self, filtro_aplicado):
        if filtro_aplicado == "daqui_a_7_dias":
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_limite_daqui_a_7_dias
        else:
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_limite
        return inclusoes_normais.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def inclusoes_normais_das_minhas_escolas_no_prazo_regular(self, filtro_aplicado):
        if filtro_aplicado == "daqui_a_30_dias":
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_regular_daqui_a_30_dias
        elif filtro_aplicado == "daqui_a_7_dias":
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_regular_daqui_a_7_dias
        else:
            inclusoes_normais = GrupoInclusaoAlimentacaoNormal.prazo_regular
        return inclusoes_normais.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

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
                             blank=True, null=True,
                             on_delete=models.SET_NULL)

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


class Codae(Nomeavel, TemChaveExterna):
    usuarios = models.ManyToManyField(Usuario, related_name='CODAE', blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Codae, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "CODAE"
        verbose_name_plural = "CODAE"
