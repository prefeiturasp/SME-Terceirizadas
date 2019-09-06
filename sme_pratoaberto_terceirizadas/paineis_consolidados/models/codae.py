from django.db import models

from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario


class SolicitacoesCODAE(models.Model):
    uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    diretoria_regional_id = models.PositiveIntegerField()
    criado_em = models.DateTimeField()
    tipo_doc = models.CharField(max_length=30)
    status_evento = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=32)

    @classmethod
    def get_pendentes_aprovacao(cls):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.DRE_APROVOU,
            status=PedidoAPartirDaEscolaWorkflow.DRE_APROVADO
        ).order_by('-criado_em')

    @classmethod
    def get_cancelados(cls):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_REPROVOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_CANCELOU_PEDIDO
        ).order_by('-criado_em')

    @classmethod
    def get_aprovados(cls):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_APROVOU,
            status=PedidoAPartirDaEscolaWorkflow.CODAE_APROVADO
        ).order_by('-criado_em')

    @classmethod
    def get_solicitacoes_revisao(cls):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_PEDE_REVISAO,
        ).order_by('-criado_em')

    class Meta:
        managed = False
        db_table = 'codae_solicitacoes'
