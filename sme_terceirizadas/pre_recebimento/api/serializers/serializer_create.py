from datetime import date

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EtapasDoCronograma,
    ProgramacaoDoRecebimentoDoCronograma
)
from sme_terceirizadas.terceirizada.models import Terceirizada


class ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(serializers.ModelSerializer):
    data_programada = serializers.CharField(required=False)
    tipo_carga = serializers.ChoiceField(
        choices=ProgramacaoDoRecebimentoDoCronograma.TIPO_CARGA_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        exclude = ('id', 'cronograma')


class EtapasDoCronogramaCreateSerializer(serializers.ModelSerializer):
    empenho_uuid = serializers.UUIDField(required=False)
    numero_empenho = serializers.CharField(required=False)
    etapa = serializers.CharField(required=False)
    parte = serializers.CharField(required=False)
    quantidade = serializers.FloatField(required=False)
    total_embalagens = serializers.IntegerField(required=False)

    class Meta:
        model = EtapasDoCronograma
        exclude = ('id', 'cronograma')


class CronogramaCreateSerializer(serializers.ModelSerializer):
    armazem = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Terceirizada.objects.all(),
        allow_null=True
    )
    contrato_uuid = serializers.UUIDField(required=True)
    contrato = serializers.CharField(required=True)
    empresa_uuid = serializers.UUIDField(required=False)
    nome_empresa = serializers.CharField(required=False)
    produto_uuid = serializers.UUIDField(required=False)
    processo_sei = serializers.CharField(required=False)
    nome_produto = serializers.CharField(required=False)
    qtd_total_programada = serializers.FloatField(required=False)
    unidade_medida = serializers.CharField(required=False)
    tipo_embalagem = serializers.ChoiceField(
        choices=Cronograma.TIPO_EMBALAGEM_CHOICES, required=False, allow_blank=True)
    etapas = EtapasDoCronogramaCreateSerializer(many=True, required=False)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(many=True, required=False)
    cadastro_finalizado = serializers.BooleanField(required=False)

    def gera_proximo_numero_cronograma(self):
        ano = date.today().year
        ultimo_cronograma = Cronograma.objects.last()
        if ultimo_cronograma:
            return f'{str(int(ultimo_cronograma.numero[:3]) + 1).zfill(3)}/{ano}'
        else:
            return f'001/{ano}'

    def create(self, validated_data):
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])
        numero_cronograma = self.gera_proximo_numero_cronograma()
        cronograma = Cronograma.objects.create(numero=numero_cronograma, **validated_data)
        cronograma.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_CRIADO, usuario=user)

        for etapa in etapas:
            EtapasDoCronograma.objects.create(
                cronograma=cronograma,
                **etapa
            )

        for programacao in programacoes_de_recebimento:
            ProgramacaoDoRecebimentoDoCronograma.objects.create(
                cronograma=cronograma,
                **programacao
            )

        if cadastro_finalizado:
            cronograma.inicia_fluxo(user=user)

        return cronograma

    class Meta:
        model = Cronograma
        exclude = ('id', 'numero', 'status')
