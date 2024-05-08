from rest_framework import serializers

from sme_terceirizadas.imr.models import PeriodoVisita


class PeriodoVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoVisita
        exclude = ("id",)
