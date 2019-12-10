from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q, Sum
from django_prometheus.models import ExportModelOperationsMixin

from ..cardapio.models import AlteracaoCardapio, GrupoSuspensaoAlimentacao, InversaoCardapio
from ..dados_comuns.behaviors import Ativavel, Iniciais, Nomeavel, TemChaveExterna, TemCodigoEOL, TemVinculos
from ..dados_comuns.constants import (
    COGESTOR,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    DAQUI_A_SETE_DIAS,
    DAQUI_A_TRINTA_DIAS,
    DIRETOR,
    SUPLENTE
)
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua
from ..kit_lanche.models import SolicitacaoKitLancheAvulsa, SolicitacaoKitLancheUnificada


class DiretoriaRegional(ExportModelOperationsMixin('diretoria_regional'), Nomeavel, Iniciais, TemChaveExterna,
                        TemCodigoEOL, TemVinculos):

    @property
    def vinculos_que_podem_ser_finalizados(self):
        return self.vinculos.filter(
            Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
            Q(data_inicial__isnull=False, data_final=None, ativo=True)  # noqa W504 ativo
        ).exclude(perfil__nome__in=[COGESTOR, SUPLENTE])

    @property
    def escolas(self):
        return self.escolas

    @property
    def quantidade_alunos(self):
        quantidade_result = self.escolas.aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum', 0)

    #
    # Inclusões continuas e normais
    #

    @property
    def inclusoes_continuas_autorizadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO,
                        GrupoInclusaoAlimentacaoNormal.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inclusoes_normais_autorizadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO,
                        GrupoInclusaoAlimentacaoNormal.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inclusoes_continuas_reprovadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_NAO_VALIDOU_PEDIDO_ESCOLA
        )

    @property
    def inclusoes_normais_reprovadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            escola__in=self.escolas.all(),
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_NAO_VALIDOU_PEDIDO_ESCOLA
        )

    # TODO: talvez fazer um manager genérico pra fazer esse filtro

    def solicitacoes_kit_lanche_das_minhas_escolas_a_validar(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            solicitacoes_kit_lanche_avulsa = SolicitacaoKitLancheAvulsa.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            solicitacoes_kit_lanche_avulsa = SolicitacaoKitLancheAvulsa.deste_mes  # type: ignore
        else:
            solicitacoes_kit_lanche_avulsa = SolicitacaoKitLancheAvulsa.objects  # type: ignore
        return solicitacoes_kit_lanche_avulsa.filter(
            escola__in=self.escolas.all(),
            status=InversaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    def alteracoes_cardapio_das_minhas_escolas_a_validar(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inversoes_cardapio = AlteracaoCardapio.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inversoes_cardapio = AlteracaoCardapio.deste_mes  # type: ignore
        else:
            inversoes_cardapio = AlteracaoCardapio.objects  # type: ignore
        return inversoes_cardapio.filter(
            escola__in=self.escolas.all(),
            status=InversaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    # TODO rever os demais métodos de alterações de cardápio, já que esse consolida todas as prioridades.
    def inclusoes_alimentacao_continua_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inclusoes_alimentacao_continuas = InclusaoAlimentacaoContinua.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inclusoes_alimentacao_continuas = InclusaoAlimentacaoContinua.deste_mes  # type: ignore
        else:
            inclusoes_alimentacao_continuas = InclusaoAlimentacaoContinua.objects  # type: ignore
        return inclusoes_alimentacao_continuas.filter(
            escola__in=self.escolas.all(),
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR
        )

    def grupos_inclusoes_alimentacao_normal_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inclusoes_alimentacao_normais = GrupoInclusaoAlimentacaoNormal.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inclusoes_alimentacao_normais = GrupoInclusaoAlimentacaoNormal.deste_mes  # type: ignore
        else:
            inclusoes_alimentacao_normais = GrupoInclusaoAlimentacaoNormal.objects  # type: ignore
        return inclusoes_alimentacao_normais.filter(
            escola__in=self.escolas.all(),
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_A_VALIDAR
        )

    #
    # Alterações de cardápio
    #

    @property
    def alteracoes_cardapio_pendentes_das_minhas_escolas(self):
        return AlteracaoCardapio.objects.filter(
            escola__in=self.escolas.all(),
            status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    @property
    def alteracoes_cardapio_autorizadas(self):
        return AlteracaoCardapio.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[AlteracaoCardapio.workflow_class.CODAE_AUTORIZADO,
                        AlteracaoCardapio.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def solicitacao_kit_lanche_avulsa_autorizadas(self):
        return SolicitacaoKitLancheAvulsa.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[SolicitacaoKitLancheAvulsa.workflow_class.CODAE_AUTORIZADO,
                        SolicitacaoKitLancheAvulsa.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def solicitacao_kit_lanche_avulsa_reprovados(self):
        return SolicitacaoKitLancheAvulsa.objects.filter(
            escola__in=self.escolas.all(),
            status=SolicitacaoKitLancheAvulsa.workflow_class.DRE_PEDIU_ESCOLA_REVISAR
        )

    @property
    def alteracoes_cardapio_reprovadas(self):
        return AlteracaoCardapio.objects.filter(
            escola__in=self.escolas.all(),
            status=AlteracaoCardapio.workflow_class.DRE_NAO_VALIDOU_PEDIDO_ESCOLA
        )

    # TODO rever os demais métodos de alterações de cardápio, já que esse consolida todas as prioridades.
    def alteracoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            alteracoes_cardapio = AlteracaoCardapio.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            alteracoes_cardapio = AlteracaoCardapio.deste_mes  # type: ignore
        else:
            alteracoes_cardapio = AlteracaoCardapio.objects  # type: ignore
        return alteracoes_cardapio.filter(
            escola__in=self.escolas.all(),
            status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    #
    # Inversões de cardápio
    #

    def inversoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inversoes_cardapio = InversaoCardapio.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inversoes_cardapio = InversaoCardapio.deste_mes  # type: ignore
        else:
            inversoes_cardapio = InversaoCardapio.objects  # type: ignore
        return inversoes_cardapio.filter(
            escola__in=self.escolas.all(),
            status=InversaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    @property
    def inversoes_cardapio_autorizadas(self):
        return InversaoCardapio.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[InversaoCardapio.workflow_class.DRE_VALIDADO,
                        InversaoCardapio.workflow_class.CODAE_AUTORIZADO,
                        InversaoCardapio.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inversoes_cardapio_reprovados(self):
        return InversaoCardapio.objects.filter(
            escola__in=self.escolas.all(),
            status__in=[InversaoCardapio.workflow_class.DRE_NAO_VALIDOU_PEDIDO_ESCOLA]
        )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Diretoria regional'
        verbose_name_plural = 'Diretorias regionais'
        ordering = ('nome',)


class FaixaIdadeEscolar(ExportModelOperationsMixin('faixa_idade'), Nomeavel, Ativavel, TemChaveExterna):
    """de 1 a 2 anos, de 2 a 5 anos, de 7 a 18 anos, etc."""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Idade escolar'
        verbose_name_plural = 'Idades escolares'
        ordering = ('nome',)


class TipoUnidadeEscolar(ExportModelOperationsMixin('tipo_ue'), Iniciais, Ativavel, TemChaveExterna):
    """EEMEF, CIEJA, EMEI, EMEBS, CEI, CEMEI..."""

    cardapios = models.ManyToManyField('cardapio.Cardapio', blank=True,
                                       related_name='tipos_unidade_escolar')
    periodos_escolares = models.ManyToManyField('escola.PeriodoEscolar', blank=True,
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
        verbose_name = 'Tipo de unidade escolar'
        verbose_name_plural = 'Tipos de unidade escolar'


class TipoGestao(ExportModelOperationsMixin('tipo_gestao'), Nomeavel, Ativavel, TemChaveExterna):
    """Terceirizada completa, tec mista."""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tipo de gestão'
        verbose_name_plural = 'Tipos de gestão'


class PeriodoEscolar(ExportModelOperationsMixin('periodo_escolar'), Nomeavel, TemChaveExterna):
    """manhã, intermediário, tarde, vespertino, noturno, integral."""

    tipos_alimentacao = models.ManyToManyField('cardapio.TipoAlimentacao', related_name='periodos_escolares')

    class Meta:
        verbose_name = 'Período escolar'
        verbose_name_plural = 'Períodos escolares'

    def __str__(self):
        return self.nome


class Escola(ExportModelOperationsMixin('escola'), Ativavel, TemChaveExterna, TemCodigoEOL, TemVinculos):
    nome = models.CharField('Nome', max_length=160, blank=True)
    codigo_eol = models.CharField('Código EOL', max_length=6, unique=True, validators=[MinLengthValidator(6)])
    quantidade_alunos = models.PositiveSmallIntegerField('Quantidade de alunos', default=1)

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
                             on_delete=models.PROTECT)
    contato = models.ForeignKey('dados_comuns.Contato', on_delete=models.DO_NOTHING,
                                blank=True, null=True)

    idades = models.ManyToManyField(FaixaIdadeEscolar, blank=True)

    @property
    def alunos_por_periodo_escolar(self):
        return self.escolas_periodos.filter(quantidade_alunos__gte=1)

    @property
    def periodos_escolares(self):
        """Recupera periodos escolares da escola, desde que haja pelomenos um aluno para este período."""
        # TODO: ver uma forma melhor de fazer essa query
        periodos_ids = self.escolas_periodos.filter(quantidade_alunos__gte=1).values_list('periodo_escolar', flat=True)
        return PeriodoEscolar.objects.filter(id__in=periodos_ids)

    @property
    def vinculos_que_podem_ser_finalizados(self):
        return self.vinculos.filter(
            Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
            Q(data_inicial__isnull=False, data_final=None, ativo=True)  # noqa W504 ativo
        ).exclude(perfil__nome=DIRETOR)

    @property
    def grupos_inclusoes(self):
        return self.grupos_inclusoes_normais

    def get_cardapio(self, data):
        return self.tipo_unidade.get_cardapio(data)

    @property
    def inclusoes_continuas(self):
        return self.inclusoes_alimentacao_continua

    def __str__(self):
        return f'{self.codigo_eol}: {self.nome}'

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        ordering = ('codigo_eol',)


class EscolaPeriodoEscolar(ExportModelOperationsMixin('escola_periodo'), Ativavel, TemChaveExterna):
    """Serve para guardar a quantidade de alunos da escola em um dado periodo escolar.

    Ex: EMEI BLABLA pela manhã tem 55 alunos
    """

    escola = models.ForeignKey(Escola,
                               related_name='escolas_periodos',
                               on_delete=models.DO_NOTHING)
    periodo_escolar = models.ForeignKey(PeriodoEscolar,
                                        related_name='escolas_periodos',
                                        on_delete=models.DO_NOTHING)
    quantidade_alunos = models.PositiveSmallIntegerField('Quantidade de alunos', default=0)

    def __str__(self):
        return f'Escola {self.escola.nome} no periodo da {self.periodo_escolar.nome} ' \
               f'tem {self.quantidade_alunos} alunos'

    class Meta:
        verbose_name = 'Escola com período escolar'
        verbose_name_plural = 'Escola com períodos escolares'
        unique_together = [['periodo_escolar', 'escola']]


class Lote(ExportModelOperationsMixin('lote'), TemChaveExterna, Nomeavel, Iniciais):
    """Lote de escolas."""

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

    @property
    def quantidade_alunos(self):
        quantidade_result = self.escolas.aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum') or 0

    def __str__(self):
        nome_dre = self.diretoria_regional.nome if self.diretoria_regional else 'sem DRE definida'
        return f'{self.nome} - {nome_dre}'

    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ('nome',)


class Subprefeitura(ExportModelOperationsMixin('subprefeitura'), Nomeavel, TemChaveExterna):
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
        verbose_name = 'Subprefeitura'
        verbose_name_plural = 'Subprefeituras'
        ordering = ('nome',)


class Codae(ExportModelOperationsMixin('codae'), Nomeavel, TemChaveExterna, TemVinculos):

    @property
    def vinculos_que_podem_ser_finalizados(self):
        return self.vinculos.filter(
            Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
            Q(data_inicial__isnull=False, data_final=None, ativo=True)  # noqa W504 ativo
        ).exclude(perfil__nome__in=[COORDENADOR_DIETA_ESPECIAL, COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA])

    @property
    def quantidade_alunos(self):
        escolas = Escola.objects.all()
        quantidade_result = escolas.aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum', 0)

    def inversoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inversoes_cardapio = InversaoCardapio.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inversoes_cardapio = InversaoCardapio.deste_mes  # type: ignore
        else:
            inversoes_cardapio = InversaoCardapio.objects  # type: ignore
        return inversoes_cardapio.filter(
            status=InversaoCardapio.workflow_class.DRE_VALIDADO
        )

    def grupos_inclusoes_alimentacao_normal_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inversoes_cardapio = GrupoInclusaoAlimentacaoNormal.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inversoes_cardapio = GrupoInclusaoAlimentacaoNormal.deste_mes  # type: ignore
        else:
            inversoes_cardapio = GrupoInclusaoAlimentacaoNormal.objects  # type: ignore
        return inversoes_cardapio.filter(
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_VALIDADO
        )

    @property
    def inversoes_cardapio_autorizadas(self):
        return InversaoCardapio.objects.filter(
            status__in=[InversaoCardapio.workflow_class.CODAE_AUTORIZADO,
                        InversaoCardapio.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inversoes_cardapio_reprovados(self):
        return InversaoCardapio.objects.filter(
            status__in=[InversaoCardapio.workflow_class.CODAE_NEGOU_PEDIDO]
        )

    def inclusoes_alimentacao_continua_das_minhas_escolas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            inversoes_cardapio = InclusaoAlimentacaoContinua.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            inversoes_cardapio = InclusaoAlimentacaoContinua.deste_mes  # type: ignore
        else:
            inversoes_cardapio = InclusaoAlimentacaoContinua.objects  # type: ignore
        return inversoes_cardapio.filter(
            status=InclusaoAlimentacaoContinua.workflow_class.DRE_VALIDADO
        )

    def alteracoes_cardapio_das_minhas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            alteracoes_cardapio = AlteracaoCardapio.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            alteracoes_cardapio = AlteracaoCardapio.deste_mes  # type: ignore
        else:
            alteracoes_cardapio = AlteracaoCardapio.objects  # type: ignore
        return alteracoes_cardapio.filter(
            status=AlteracaoCardapio.workflow_class.DRE_VALIDADO
        )

    def suspensoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        return GrupoSuspensaoAlimentacao.objects.filter(
            ~Q(status__in=[GrupoSuspensaoAlimentacao.workflow_class.RASCUNHO])
        )

        #
        # Inversões de cardápio
        #

    def solicitacoes_unificadas(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            solicitacoes_unificadas = SolicitacaoKitLancheUnificada.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            solicitacoes_unificadas = SolicitacaoKitLancheUnificada.deste_mes  # type: ignore
        else:
            solicitacoes_unificadas = SolicitacaoKitLancheUnificada.objects  # type: ignore
        return solicitacoes_unificadas.filter(
            status=SolicitacaoKitLancheUnificada.workflow_class.CODAE_A_AUTORIZAR
        )

    @property
    def solicitacoes_unificadas_autorizadas(self):
        return SolicitacaoKitLancheUnificada.objects.filter(
            status__in=[SolicitacaoKitLancheUnificada.workflow_class.CODAE_AUTORIZADO,
                        SolicitacaoKitLancheUnificada.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inclusoes_continuas_autorizadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            status__in=[InclusaoAlimentacaoContinua.workflow_class.CODAE_AUTORIZADO,
                        SolicitacaoKitLancheUnificada.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inclusoes_normais_autorizadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            status__in=[GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO,
                        GrupoInclusaoAlimentacaoNormal.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def inclusoes_continuas_reprovadas(self):
        return InclusaoAlimentacaoContinua.objects.filter(
            status=InclusaoAlimentacaoContinua.workflow_class.CODAE_NEGOU_PEDIDO
        )

    @property
    def inclusoes_normais_reprovadas(self):
        return GrupoInclusaoAlimentacaoNormal.objects.filter(
            status=GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_NEGOU_PEDIDO
        )

    @property
    def solicitacao_kit_lanche_avulsa_autorizadas(self):
        return SolicitacaoKitLancheAvulsa.objects.filter(
            status__in=[SolicitacaoKitLancheAvulsa.workflow_class.CODAE_AUTORIZADO,
                        SolicitacaoKitLancheAvulsa.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def solicitacao_kit_lanche_avulsa_reprovadas(self):
        return SolicitacaoKitLancheAvulsa.objects.filter(
            status=SolicitacaoKitLancheAvulsa.workflow_class.CODAE_NEGOU_PEDIDO
        )

    # TODO: talvez fazer um manager genérico pra fazer esse filtro

    def solicitacoes_kit_lanche_das_minhas_escolas_a_validar(self, filtro_aplicado):
        if filtro_aplicado == DAQUI_A_SETE_DIAS:
            solicitacoes_kit_lanche = SolicitacaoKitLancheAvulsa.desta_semana
        elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
            solicitacoes_kit_lanche = SolicitacaoKitLancheAvulsa.deste_mes  # type: ignore
        else:
            solicitacoes_kit_lanche = SolicitacaoKitLancheAvulsa.objects  # type: ignore
        return solicitacoes_kit_lanche.filter(
            status=InversaoCardapio.workflow_class.DRE_VALIDADO
        )

    @property
    def alteracoes_cardapio_autorizadas(self):
        return AlteracaoCardapio.objects.filter(
            status__in=[AlteracaoCardapio.workflow_class.CODAE_AUTORIZADO,
                        AlteracaoCardapio.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA]
        )

    @property
    def alteracoes_cardapio_reprovadas(self):
        return AlteracaoCardapio.objects.filter(
            status=AlteracaoCardapio.workflow_class.CODAE_NEGOU_PEDIDO
        )

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
        verbose_name = 'CODAE'
        verbose_name_plural = 'CODAE'
