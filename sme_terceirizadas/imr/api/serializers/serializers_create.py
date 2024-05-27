from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.imr.models import (
    FormularioOcorrenciasBase,
    FormularioSupervisao,
    PeriodoVisita,
    TipoOcorrencia,
    OcorrenciaNaoSeAplica,
    ParametrizacaoOcorrencia,
    RespostaDatas,
    RespostaCampoTextoLongo,
    RespostaCampoTextoSimples,
    RespostaCampoNumerico,
    RespostaSimNao
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


class RespostaDatasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespostaDatas
        exclude = ("id",)


class RespostaCampoTextoLongoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespostaCampoTextoLongo
        exclude = ("id",)


class RespostaCampoTextoSimplesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespostaCampoTextoSimples
        exclude = ("id",)


class RespostaCampoNumericoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespostaCampoNumerico
        exclude = ("id",)


class RespostaSimNaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespostaSimNao
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
    ocorrencias = serializers.ListField(required=False, allow_null=True)

    def validate(self, attrs):
        data = attrs.get("data", None)

        if not data:
            raise serializers.ValidationError({"data": ["Este campo é obrigatório!"]})

        return attrs

    def create(self, validated_data):
        usuario = self.context["request"].user
        data_visita = validated_data.pop("data", None)
        ocorrencias_nao_se_aplica = validated_data.pop("ocorrencias_nao_se_aplica", [])
        ocorrencias = validated_data.pop("ocorrencias", [])

        form_base = FormularioOcorrenciasBase.objects.create(
            usuario=usuario, data=data_visita
        )

        form_supervisao = FormularioSupervisao.objects.create(
            formulario_base=form_base, **validated_data
        )

        self.create_ocorrencias_nao_se_aplica(ocorrencias_nao_se_aplica, form_base)

        self.create_ocorrencias(ocorrencias, form_base)

        return form_supervisao

    def create_ocorrencias_nao_se_aplica(self, ocorrencias_data, form_base):
        for ocorrencia_data in ocorrencias_data:
            ocorrencia_data["formulario_base"] = str(form_base.uuid)
            serializer = OcorrenciaNaoSeAplicaCreateSerializer(data=ocorrencia_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError(
                    {"ocorrencias_nao_se_aplica": serializer.errors}
                )

    def get_serializer_class_by_name(self, name):
        serializer_class = globals().get(name)
        if serializer_class is None:
            raise ValueError(f"Nenhum serializer encontrado com o nome '{name}'")
        return serializer_class

    def create_ocorrencias(self, ocorrencias_data, form_base):
        for ocorrencia_data in ocorrencias_data:
            ocorrencia_data["formulario_base"] = form_base.pk
            parametrizacao_UUID = ocorrencia_data["parametrizacao"]

            try:
                parametrizacao = ParametrizacaoOcorrencia.objects.get(uuid=parametrizacao_UUID)
            except ParametrizacaoOcorrencia.DoesNotExist:
                raise serializers.ValidationError({
                    "detail": f"ParametrizacaoOcorrencia com o UUID {parametrizacao_UUID} não foi encontrada"
                })

            ocorrencia_data["parametrizacao"] = parametrizacao.pk

            response_model_class_name = parametrizacao.tipo_pergunta.get_model_tipo_resposta().__name__
            response_serializer = self.get_serializer_class_by_name(f"{response_model_class_name}CreateSerializer")

            serializer = response_serializer(data=ocorrencia_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError({
                    "parametrizacao": parametrizacao.uuid,
                    "error": serializer.errors
                })

    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)
