from rest_framework import serializers

from sme_terceirizadas.imr.models import FormularioSupervisao, PeriodoVisita


class PeriodoVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoVisita
        exclude = ("id",)


class FormularioSupervisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)
