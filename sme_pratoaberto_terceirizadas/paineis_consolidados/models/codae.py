from django.db import models

from ...dados_comuns.fluxo_status import PedidoAPartirDaDiretoriaRegionalWorkflow, PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario


class MoldeConsolidado(models.Model):
    uuid = models.UUIDField(editable=False)
    escola_uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    dre_uuid = models.UUIDField(editable=False)
    criado_em = models.DateTimeField()
    tipo_doc = models.CharField(max_length=30)
    desc_doc = models.CharField(max_length=50)
    status_evento = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=32)

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

    class Meta:
        managed = False
        db_table = 'solicitacoes_consolidadas'
        abstract = True


class SolicitacoesCODAE(MoldeConsolidado):

    @classmethod
    def get_pendentes_aprovacao(cls, **kwargs):
        return cls.objects.filter(
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
        return cls.objects.filter(escola_uuid=escola_uuid).exclude(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU).exclude(
            status=PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO).order_by('-criado_em')

    @classmethod
    def get_autorizados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
            escola_uuid=escola_uuid
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
            status=cls._WORKFLOW_CLASS.CODAE_A_AUTORIZAR,
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
