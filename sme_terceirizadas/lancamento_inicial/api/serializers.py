from rest_framework import serializers

from ..models import LancamentoDiario, Refeicao

class LancamentoDiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LancamentoDiario
        exclude = ('id',)


class RefeicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refeicao
        exclude = ('id',)
