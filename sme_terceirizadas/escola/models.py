import logging
from collections import Counter
from datetime import date

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q, Sum
from django_prometheus.models import ExportModelOperationsMixin

from ..cardapio.models import AlteracaoCardapio, GrupoSuspensaoAlimentacao, InversaoCardapio
from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Iniciais,
    Justificativa,
    Nomeavel,
    TemChaveExterna,
    TemCodigoEOL,
    TemVinculos
)
from ..dados_comuns.constants import (
    COGESTOR,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    DIRETOR,
    SUPLENTE
)
from ..dados_comuns.utils import queryset_por_data, subtrai_meses_de_data
from ..eol_servico.utils import EOLService, dt_nascimento_from_api
from ..escola.constants import PERIODOS_ESPECIAIS_CEI_CEU_CCI
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua, InclusaoAlimentacaoDaCEI
from ..kit_lanche.models import SolicitacaoKitLancheAvulsa, SolicitacaoKitLancheUnificada

logger = logging.getLogger('sigpae.EscolaModels')


class DiretoriaRegional(ExportModelOperationsMixin('diretoria_regional'), Nomeavel, Iniciais, TemChaveExterna,
                        TemCodigoEOL, TemVinculos):

    @property
    def vinculos_que_podem_ser_finalizados(self):
        return self.vinculos.filter(
            Q(data_inicial=None, data_final=None, ativo=False) |  # noqa W504 esperando ativacao
            Q(data_inicial__isnull=False, data_final=None, ativo=True)  # noqa W504 ativo
        ).exclude(perfil__nome__in=[COGESTOR, SUPLENTE])

    @property
    def quantidade_alunos(self):
        quantidade_result = EscolaPeriodoEscolar.objects.filter(
            escola__in=self.escolas.all()
        ).aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum') or 0

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

    def filtra_solicitacoes_minhas_escolas_a_validar_por_data(self, filtro_aplicado, model):
        queryset = queryset_por_data(filtro_aplicado, model)
        return queryset.filter(
            escola__in=self.escolas.all(),
            status=SolicitacaoKitLancheAvulsa.workflow_class.DRE_A_VALIDAR
        )

    def solicitacoes_kit_lanche_das_minhas_escolas_a_validar(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            SolicitacaoKitLancheAvulsa
        )

    def alteracoes_cardapio_das_minhas_escolas_a_validar(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            AlteracaoCardapio
        )

    def inclusoes_alimentacao_continua_das_minhas_escolas(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            InclusaoAlimentacaoContinua
        )

    def grupos_inclusoes_alimentacao_normal_das_minhas_escolas(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            GrupoInclusaoAlimentacaoNormal
        )

    def inclusoes_alimentacao_de_cei_das_minhas_escolas(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            InclusaoAlimentacaoDaCEI
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

    def alteracoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, AlteracaoCardapio)
        return queryset.filter(
            escola__in=self.escolas.all(),
            status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR
        )

    #
    # Inversões de cardápio
    #

    def inversoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, InversaoCardapio)
        return queryset.filter(
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
    tem_somente_integral_e_parcial = models.BooleanField(
        help_text='Variável de controle para setar os períodos escolares na mão, válido para CEI CEU, CEI e CCI',
        default=False
    )

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
    def quantidade_alunos(self):
        quantidade_result = self.escolas_periodos.aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum') or 0

    @property
    def alunos_por_periodo_escolar(self):
        return self.escolas_periodos.filter(quantidade_alunos__gte=1)

    @property
    def periodos_escolares(self):
        """Recupera periodos escolares da escola, desde que haja pelomenos um aluno para este período."""
        if self.tipo_unidade.tem_somente_integral_e_parcial:
            periodos = PeriodoEscolar.objects.filter(nome__in=PERIODOS_ESPECIAIS_CEI_CEU_CCI)
        else:
            # TODO: ver uma forma melhor de fazer essa query
            periodos_ids = self.escolas_periodos.filter(
                quantidade_alunos__gte=1).values_list(
                'periodo_escolar', flat=True
            )
            periodos = PeriodoEscolar.objects.filter(id__in=periodos_ids)
        return periodos

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
        periodo_nome = self.periodo_escolar.nome

        return f'Escola {self.escola.nome} no periodo da {periodo_nome} tem {self.quantidade_alunos} alunos'

    def alunos_por_faixa_etaria(self, data_referencia):  # noqa C901
        """
        Calcula quantos alunos existem em cada faixa etaria nesse período.

        Retorna um collections.Counter, onde as chaves são o uuid das faixas etárias
        e os valores os totais de alunos. Exemplo:
        {
            'asdf-1234': 25,
            'qwer-5678': 42,
            'zxcv-4567': 16
        }
        """
        faixas_etarias = FaixaEtaria.objects.filter(ativo=True)
        if faixas_etarias.count() == 0:
            raise ObjectDoesNotExist()
        lista_alunos = EOLService.get_informacoes_escola_turma_aluno(
            self.escola.codigo_eol
        )
        faixa_alunos = Counter()
        for aluno in lista_alunos:
            if aluno['dc_tipo_turno'].strip().upper() == self.periodo_escolar.nome:
                data_nascimento = dt_nascimento_from_api(aluno['dt_nascimento_aluno'])
                for faixa_etaria in faixas_etarias:
                    if faixa_etaria.data_pertence_a_faixa(data_nascimento, data_referencia):
                        faixa_alunos[faixa_etaria.uuid] += 1

        return faixa_alunos

    class Meta:
        verbose_name = 'Escola com período escolar'
        verbose_name_plural = 'Escola com períodos escolares'
        unique_together = [['periodo_escolar', 'escola']]


class LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar(TemChaveExterna, CriadoEm, Justificativa, CriadoPor):
    escola = models.ForeignKey(Escola,
                               related_name='log_alteracao_quantidade_alunos',
                               on_delete=models.DO_NOTHING)
    periodo_escolar = models.ForeignKey(PeriodoEscolar,
                                        related_name='log_alteracao_quantidade_alunos',
                                        on_delete=models.DO_NOTHING)
    quantidade_alunos_de = models.PositiveSmallIntegerField('Quantidade de alunos anterior', default=0)
    quantidade_alunos_para = models.PositiveSmallIntegerField('Quantidade de alunos alterada', default=0)

    def __str__(self):
        quantidade_anterior = self.quantidade_alunos_de
        quantidade_atual = self.quantidade_alunos_para
        escola = self.escola.nome
        return f'Alteração de: {quantidade_anterior} alunos, para: {quantidade_atual} alunos na escola: {escola}'

    class Meta:
        verbose_name = 'Log Alteração quantidade de alunos'
        verbose_name_plural = 'Logs de Alteração quantidade de alunos'
        ordering = ('criado_em',)


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
        quantidade_result = EscolaPeriodoEscolar.objects.filter(
            escola__in=self.escolas.all()
        ).aggregate(Sum('quantidade_alunos'))
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
        quantidade_result = EscolaPeriodoEscolar.objects.filter(
            escola__in=Escola.objects.all()
        ).aggregate(Sum('quantidade_alunos'))
        return quantidade_result.get('quantidade_alunos__sum') or 0

    def inversoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, InversaoCardapio)
        return queryset.filter(
            status=InversaoCardapio.workflow_class.DRE_VALIDADO
        )

    def grupos_inclusoes_alimentacao_normal_das_minhas_escolas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, GrupoInclusaoAlimentacaoNormal)
        return queryset.filter(
            status__in=[GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_VALIDADO,
                        GrupoInclusaoAlimentacaoNormal.workflow_class.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO]
        )

    def inclusoes_alimentacao_de_cei_das_minhas_escolas(self, filtro_aplicado):
        return self.filtra_solicitacoes_minhas_escolas_a_validar_por_data(
            filtro_aplicado,
            InclusaoAlimentacaoDaCEI
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
        queryset = queryset_por_data(filtro_aplicado, InclusaoAlimentacaoContinua)
        return queryset.filter(
            status__in=[GrupoInclusaoAlimentacaoNormal.workflow_class.DRE_VALIDADO,
                        GrupoInclusaoAlimentacaoNormal.workflow_class.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO]
        )

    def alteracoes_cardapio_das_minhas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, AlteracaoCardapio)
        return queryset.filter(
            status__in=[AlteracaoCardapio.workflow_class.DRE_VALIDADO,
                        AlteracaoCardapio.workflow_class.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO]
        )

    def suspensoes_cardapio_das_minhas_escolas(self, filtro_aplicado):
        return GrupoSuspensaoAlimentacao.objects.filter(
            ~Q(status__in=[GrupoSuspensaoAlimentacao.workflow_class.RASCUNHO])
        )

        #
        # Inversões de cardápio
        #

    def solicitacoes_unificadas(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, SolicitacaoKitLancheUnificada)
        return queryset.filter(
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

    def solicitacoes_kit_lanche_das_minhas_escolas_a_validar(self, filtro_aplicado):
        queryset = queryset_por_data(filtro_aplicado, SolicitacaoKitLancheAvulsa)
        return queryset.filter(
            status__in=[SolicitacaoKitLancheAvulsa.workflow_class.DRE_VALIDADO,
                        SolicitacaoKitLancheAvulsa.workflow_class.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO]
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


class Aluno(TemChaveExterna):
    nome = models.CharField('Nome Completo do Aluno', max_length=100)
    codigo_eol = models.CharField('Código EOL', max_length=7, unique=True, validators=[MinLengthValidator(7)])
    data_nascimento = models.DateField()
    escola = models.ForeignKey(Escola, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.nome} - {self.codigo_eol}'

    @property
    def possui_dieta_especial_ativa(self):
        return self.dietas_especiais.filter(ativo=True).exists()

    def inativar_dieta_especial(self):
        try:
            dieta_especial = self.dietas_especiais.get(ativo=True)
            dieta_especial.ativo = False
            dieta_especial.save()
        except MultipleObjectsReturned:
            logger.critical(f'Aluno não deve possuir mais de uma Dieta Especial ativa')

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class FaixaEtaria(Ativavel, TemChaveExterna):
    inicio = models.PositiveSmallIntegerField()
    fim = models.PositiveSmallIntegerField()

    def data_pertence_a_faixa(self, data_pesquisada, data_referencia_arg=None):
        data_referencia = date.today() if data_referencia_arg is None else data_referencia_arg
        data_inicio = subtrai_meses_de_data(self.fim, data_referencia)
        data_fim = subtrai_meses_de_data(self.inicio, data_referencia)
        return data_inicio <= data_pesquisada < data_fim


class MudancaFaixasEtarias(Justificativa, TemChaveExterna):
    faixas_etarias_ativadas = models.ManyToManyField(FaixaEtaria)
