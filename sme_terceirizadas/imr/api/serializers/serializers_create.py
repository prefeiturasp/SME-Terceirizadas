from rest_framework import serializers

from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.imr.models import (
    FormularioOcorrenciasBase,
    FormularioSupervisao,
    PeriodoVisita,
    TipoOcorrencia,
    OcorrenciaNaoSeAplica
)


class OcorrenciaNaoSeAplicaCreateSerializer(serializers.ModelSerializer):
    tipo_ocorrencia = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        allow_null=True,
        queryset=TipoOcorrencia.objects.all(),
    )
    formulario_base = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        allow_null=True,
        queryset=FormularioOcorrenciasBase.objects.all(),
    )

    class Meta:
        model = OcorrenciaNaoSeAplica
        exclude = ("id",)


class FormularioSupervisaoRascunhoCreateSerializer(serializers.ModelSerializer):
    data = serializers.DateField(required=False, allow_null=True)
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
    ocorrencias_nao_se_aplica = serializers.ListField(required=False, allow_null=True)

    def validate(self, attrs):
        data = attrs.get("data", None)

        if not data:
            raise serializers.ValidationError({"data": ["Este campo é obrigatório!"]})

        return attrs

    def create(self, validated_data):
        usuario = self.context["request"].user
        data_visita = validated_data.pop("data", None)
        ocorrencias_nao_se_aplica = validated_data.pop("ocorrencias_nao_se_aplica", [])

        form_base = FormularioOcorrenciasBase.objects.create(
            usuario=usuario, data=data_visita
        )

        form_supervisao = FormularioSupervisao.objects.create(
            formulario_base=form_base, **validated_data
        )

        self.create_ocorrencias_nao_se_aplica(ocorrencias_nao_se_aplica, form_base)

        return form_supervisao

    def create_ocorrencias_nao_se_aplica(self, occurrences_data, form_base):
        for occurrence_data in occurrences_data:
            occurrence_data["formulario_base"] = str(form_base.uuid)
            serializer = OcorrenciaNaoSeAplicaCreateSerializer(data=occurrence_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError(
                    {"ocorrencias_nao_se_aplica": serializer.errors}
                )

    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)
