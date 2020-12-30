from rest_framework import serializers

from ...dieta_especial.api.serializers import ClassificacaoDietaSerializer
from ...escola.models import EscolaPeriodoEscolar
from ..models import LancamentoDiario, Refeicao


class RefeicaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refeicao
        exclude = ('id', 'lancamento')


class RefeicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refeicao
        exclude = ('id',)


class LancamentoDiarioSerializer(serializers.ModelSerializer):
    refeicoes = RefeicaoSerializer(many=True, required=False)
    tipo_dieta = ClassificacaoDietaSerializer()
    merenda_seca_solicitada = serializers.IntegerField(read_only=True)
    kits_lanches = serializers.IntegerField(read_only=True)
    troca = serializers.CharField(read_only=True)

    class Meta:
        model = LancamentoDiario
        exclude = ('id',)


class LancamentoDiarioCreateSerializer(serializers.ModelSerializer):
    refeicoes = RefeicaoCreateSerializer(many=True, required=False)
    escola_periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=EscolaPeriodoEscolar.objects.all()
    )

    def create(self, validated_data):
        refeicoes = validated_data.pop('refeicoes', [])

        try:
            lancamento = LancamentoDiario.objects.get(
                data=validated_data['data'],
                escola_periodo_escolar=validated_data['escola_periodo_escolar'],
                tipo_dieta=validated_data['tipo_dieta'] if 'tipo_dieta' in validated_data else None
            )
            self.update(lancamento, validated_data)
        except LancamentoDiario.DoesNotExist:
            lancamento = LancamentoDiario.objects.create(**validated_data)

        lancamento.refeicoes.all().delete()

        for refeicao in refeicoes:
            refeicao['lancamento'] = lancamento
            Refeicao.objects.create(**refeicao)

        return lancamento

    class Meta:
        model = LancamentoDiario
        exclude = ('id',)
