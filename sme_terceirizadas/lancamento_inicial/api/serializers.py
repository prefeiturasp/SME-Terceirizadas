from rest_framework import serializers

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

        lancamento, created = LancamentoDiario.objects.get_or_create(**validated_data)

        lancamento.refeicoes.all().delete()

        for refeicao in refeicoes:
            refeicao['lancamento'] = lancamento
            Refeicao.objects.create(**refeicao)

        return lancamento

    class Meta:
        model = LancamentoDiario
        exclude = ('id',)
