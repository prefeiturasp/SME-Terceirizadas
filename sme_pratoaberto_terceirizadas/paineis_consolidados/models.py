from django.db import models


class SolicitacoesDRE(models.Model):
    uuid = models.UUIDField(editable=False)
    lote = models.CharField(max_length=50)
    diretoria_regional_id = models.PositiveIntegerField()
    data = models.DateTimeField()
    tipo_doc = models.CharField(max_length=30)

    class Meta:
        managed = False
        abstract = True


class SolicitacoesAutorizadasDRE(SolicitacoesDRE):

    class Meta:
        managed = False
        db_table = "dre_solicitacoes_autorizadas"


class SolicitacoesPendentesDRE(SolicitacoesDRE):

    class Meta:
        managed = False
        db_table = "dre_solicitacoes_pendentes"

