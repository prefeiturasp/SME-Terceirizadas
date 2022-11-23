from rest_framework import serializers

from sme_terceirizadas.pre_recebimento.models import (
    ContatoLaboratorio,
    Cronograma,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma
)
from sme_terceirizadas.terceirizada.api.serializers.serializers import DistribuidorSimplesSerializer


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
        fields = ('uuid', 'empenho_uuid', 'numero_empenho', 'etapa', 'parte', 'data_programada', 'quantidade',
                  'total_embalagens')


class CronogramaSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(many=True)
    armazem = DistribuidorSimplesSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'criado_em', 'alterado_em', 'contrato_uuid', 'contrato', 'empresa_uuid',
                          'nome_empresa', 'processo_sei', 'produto_uuid', 'nome_produto', 'qtd_total_programada',
                          'unidade_medida', 'tipo_embalagem', 'armazem', 'etapas', 'programacoes_de_recebimento')


class CronogramaRascunhosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'alterado_em')


class ContatoLaboratorioSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContatoLaboratorio
        exclude = ('id', )


class LaboratorioSerializer(serializers.ModelSerializer):
    contatos = ContatoLaboratorioSerializer(many=True)

    class Meta:
        model = Laboratorio
        exclude = ('id', )
