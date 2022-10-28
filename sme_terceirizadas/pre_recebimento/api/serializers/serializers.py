from rest_framework import serializers

from sme_terceirizadas.pre_recebimento.models import Cronograma


class CronogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        exclude = ('id',)
