from django.db import models


class SolicitacoesCODAE(models.Model):
    uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    diretoria_regional_id = models.PositiveIntegerField()
    data = models.DateTimeField()
    tipo_doc = models.CharField(max_length=30)

    class Meta:
        managed = False
        abstract = True


class SolicitacoesAutorizadasCODAE(SolicitacoesCODAE):
    class Meta:
        managed = False
        db_table = "codae_solicitacoes_autorizadas"


class SolicitacoesPendentesCODAE(SolicitacoesCODAE):
    class Meta:
        managed = False
        db_table = "codae_solicitacoes_autorizadas"


class SolicitacoesCanceladasCODAE(SolicitacoesCODAE):
    class Meta:
        managed = False
        db_table = "codae_solicitacoes_canceladas"


class SolicitacoesRevisaoCODAE(SolicitacoesCODAE):
    class Meta:
        managed = False
        db_table = "codae_solicitacoes_revisao"
