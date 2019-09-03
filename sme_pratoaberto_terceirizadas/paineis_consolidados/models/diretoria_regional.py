import datetime
from django.db import models

from ...dados_comuns.utils import obter_dias_uteis_apos_hoje


class SolicitacoesDRE7DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=0)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=8)
        return super(SolicitacoesDRE7DiasManager, self).get_queryset().filter(data_doc__range=(data_limite_inicial, data_limite_final))


class SolicitacoesDRE30DiasManager(models.Manager):
    def get_queryset(self):
        data_limite_inicial = obter_dias_uteis_apos_hoje(quantidade_dias=0)
        data_limite_final = obter_dias_uteis_apos_hoje(quantidade_dias=31)
        return super(SolicitacoesDRE30DiasManager, self).get_queryset().filter(
            data_doc__range=(data_limite_inicial, data_limite_final))


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
    data_doc = models.DateField()

    objects = models.Manager()
    sem_filtro = models.Manager()
    filtro_7_dias = SolicitacoesDRE7DiasManager()
    filtro_30_dias = SolicitacoesDRE30DiasManager()

    class Meta:
        managed = False
        db_table = "dre_solicitacoes_pendentes"

    @property
    def prioridade(self):
        descricao = 'VENCIDO'
        data = self.data.date()
        prox_2_dias_uteis = obter_dias_uteis_apos_hoje(2)
        prox_3_dias_uteis = obter_dias_uteis_apos_hoje(3)
        prox_5_dias_uteis = obter_dias_uteis_apos_hoje(5)
        prox_6_dias_uteis = obter_dias_uteis_apos_hoje(6)
        hoje = datetime.date.today()

        if hoje <= data <= prox_2_dias_uteis:
            descricao = 'PRIORITARIO'
        elif prox_5_dias_uteis >= data >= prox_3_dias_uteis:
            descricao = 'LIMITE'
        elif data >= prox_6_dias_uteis:
            descricao = 'REGULAR'
        return descricao
