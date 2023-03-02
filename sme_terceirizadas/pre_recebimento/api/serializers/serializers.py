import datetime

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSimplesSerializer
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma
)
from sme_terceirizadas.produto.api.serializers.serializers import NomeDeProdutoEditalSerializer, UnidadeMedidaSerialzer
from sme_terceirizadas.terceirizada.api.serializers.serializers import (
    ContratoSimplesSerializer,
    DistribuidorSimplesSerializer,
    TerceirizadaSimplesSerializer
)


class ProgramacaoDoRecebimentoDoCronogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        fields = ('uuid', 'data_programada', 'tipo_carga',)


class EtapasDoCronogramaSerializer(serializers.ModelSerializer):
    data_programada = serializers.SerializerMethodField()

    def get_data_programada(self, obj):
        return obj.data_programada.strftime('%d/%m/%Y') if obj.data_programada else None

    class Meta:
        model = EtapasDoCronograma
        fields = ('uuid', 'numero_empenho', 'etapa', 'parte', 'data_programada', 'quantidade',
                  'total_embalagens')


class CronogramaSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(many=True)
    armazem = DistribuidorSimplesSerializer()
    status = serializers.CharField(source='get_status_display')
    empresa = TerceirizadaSimplesSerializer()
    contrato = ContratoSimplesSerializer()
    produto = NomeDeProdutoEditalSerializer()
    unidade_medida = UnidadeMedidaSerialzer()

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'criado_em', 'alterado_em', 'contrato', 'empresa',
                          'produto', 'qtd_total_programada', 'unidade_medida',
                          'tipo_embalagem', 'armazem', 'etapas', 'programacoes_de_recebimento')


class CronogramaRascunhosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'alterado_em')


class PainelCronogramaSerializer(serializers.ModelSerializer):
    produto = serializers.SerializerMethodField()
    empresa = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    def get_produto(self, obj):
        return obj.produto.nome if obj.produto else None

    def get_empresa(self, obj):
        return obj.empresa.razao_social if obj.empresa else None

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'empresa', 'produto', 'log_mais_recente')


class LaboratorioSerializer(serializers.ModelSerializer):
    contatos = ContatoSimplesSerializer(many=True)

    class Meta:
        model = Laboratorio
        exclude = ('id', )


class EmbalagemQldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbalagemQld
        exclude = ('id', )
