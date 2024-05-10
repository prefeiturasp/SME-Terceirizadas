from rest_framework import serializers

from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.imr.models import (
    FormularioOcorrenciasBase,
    FormularioSupervisao,
    PeriodoVisita,
)


class FormularioSupervisaoRascunhoCreateSerializer(serializers.ModelSerializer):
    data = serializers.DateField(required=True, allow_null=False)
    escola = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        allow_null=True,
        queryset=Escola.objects.all(),
    )
    periodo_visita = serializers.SlugRelatedField(
        slug_field="uuid",
        required=False,
        allow_null=True,
        queryset=PeriodoVisita.objects.all(),
    )
    nome_nutricionista_empresa = serializers.CharField(required=False, allow_null=True)
    acompanhou_visita = serializers.BooleanField(required=False)
    formulario_base = serializers.SlugRelatedField(
        slug_field="uuid",
        required=False,
        allow_null=True,
        queryset=FormularioOcorrenciasBase.objects.all(),
    )

    def create(self, validated_data):
        usuario = self.context["request"].user
        data_visita = validated_data.pop("data", None)

        form_base = FormularioOcorrenciasBase.objects.create(
            usuario=usuario, data=data_visita
        )

        form_supervisao = FormularioSupervisao.objects.create(
            formulario_base=form_base, **validated_data
        )

        return form_supervisao

    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)
