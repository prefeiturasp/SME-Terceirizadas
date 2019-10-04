from django.db import models
from django.db.models import Q

from ...dados_comuns.constants import DAQUI_A_30_DIAS, DAQUI_A_7_DIAS
from ...dados_comuns.fluxo_status import PedidoAPartirDaDiretoriaRegionalWorkflow, PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...dados_comuns.models_abstract import TemPrioridade
from ...dados_comuns.utils import obter_dias_uteis_apos_hoje


class Solicitacoes7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=0)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=8)
        return super(Solicitacoes7DiasManager, self).get_queryset().filter(data_doc__range=(data_limite_inicial,
                                                                                            data_limite_final))


class Solicitacoes30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=0)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=31)
        return super(Solicitacoes30DiasManager, self).get_queryset().filter(
            data_doc__range=(data_limite_inicial, data_limite_final))


class MoldeConsolidado(models.Model, TemPrioridade):
    uuid = models.UUIDField(editable=False)
    escola_uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    dre_uuid = models.UUIDField(editable=False)
    dre_nome = models.CharField(max_length=200)
    criado_em = models.DateTimeField()
    data_doc = models.DateField()
    tipo_doc = models.CharField(max_length=30)
    desc_doc = models.CharField(max_length=50)
    status_evento = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=32)

    objects = models.Manager()
    sem_filtro = models.Manager()
    filtro_7_dias = Solicitacoes7DiasManager()
    filtro_30_dias = Solicitacoes30DiasManager()

    @classmethod
    def get_pendentes_aprovacao(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_negados(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_autorizados(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_solicitacoes_revisao(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @property
    def data(self):
        return self.data_doc

    class Meta:
        managed = False
        db_table = 'solicitacoes_consolidadas'
        abstract = True


class SolicitacoesCODAE(MoldeConsolidado):

    @classmethod
    def get_pendentes_aprovacao(cls, **kwargs):
        filtro = kwargs.get('filtro')
        manager = cls.sem_filtro
        if filtro == DAQUI_A_7_DIAS:
            manager = cls.filtro_7_dias
        elif filtro == DAQUI_A_30_DIAS:
            manager = cls.filtro_30_dias
        return manager.filter(
            status_evento=LogSolicitacoesUsuario.DRE_VALIDOU,
            status=PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
        ).order_by('-criado_em')

    @classmethod
    def get_negados(cls, **kwargs):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO
        ).order_by('-criado_em')

    @classmethod
    def get_autorizados(cls, **kwargs):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
        ).order_by('-criado_em')

    @classmethod
    def get_solicitacoes_revisao(cls, **kwargs):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_PEDIU_REVISAO,
        ).order_by('-criado_em')


class SolicitacoesEscola(MoldeConsolidado):

    @classmethod
    def get_pendentes_aprovacao(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            escola_uuid=escola_uuid
        ).filter(
            Q(status=PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
              status_evento=LogSolicitacoesUsuario.INICIO_FLUXO) |  # noqa W504
            Q(status=PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
              status_evento=LogSolicitacoesUsuario.DRE_VALIDOU)
        ).order_by('-criado_em')

    @classmethod
    def get_autorizados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            escola_uuid=escola_uuid
        ).filter(
            Q(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
              status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO) |  # noqa W504
            Q(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
              status=PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA)
        ).order_by('-criado_em')

    @classmethod
    def get_negados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO,
            escola_uuid=escola_uuid
        ).order_by('-criado_em')

    @classmethod
    def get_cancelados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.ESCOLA_CANCELOU,
            status=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
            escola_uuid=escola_uuid
        ).order_by('-criado_em')


class SolicitacoesDRE(MoldeConsolidado):
    _WORKFLOW_CLASS = PedidoAPartirDaDiretoriaRegionalWorkflow

    @classmethod
    def get_pendentes_aprovacao(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status__in=[cls._WORKFLOW_CLASS.CODAE_A_AUTORIZAR, PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO],
            dre_uuid=dre_uuid
        ).order_by('-criado_em')

    @classmethod
    def get_autorizados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
            status=cls._WORKFLOW_CLASS.CODAE_AUTORIZADO,
            dre_uuid=dre_uuid
        ).order_by('-criado_em')

    @classmethod
    def get_negados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status=cls._WORKFLOW_CLASS.CODAE_NEGOU_PEDIDO,
            dre_uuid=dre_uuid
        ).order_by('-criado_em')

    @classmethod
    def get_cancelados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.DRE_CANCELOU,
            status=cls._WORKFLOW_CLASS.DRE_CANCELOU,
            dre_uuid=dre_uuid
        ).order_by('-criado_em')
