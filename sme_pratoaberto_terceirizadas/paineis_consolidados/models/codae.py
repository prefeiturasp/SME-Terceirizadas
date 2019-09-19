from django.db import models

from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario


class MoldeConsolidado(models.Model):
    uuid = models.UUIDField(editable=False)
    escola_uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    diretoria_regional_id = models.PositiveIntegerField()
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
        db_table = 'codae_solicitacoes'
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
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.DRE_VALIDOU,
            status=PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
            escola_uuid=escola_uuid
        ).order_by('-criado_em')

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
