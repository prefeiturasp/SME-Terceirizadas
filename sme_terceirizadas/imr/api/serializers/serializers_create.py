import copy
import datetime

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile
from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.imr.models import (
    AnexosFormularioBase,
    FormularioDiretor,
    FormularioOcorrenciasBase,
    FormularioSupervisao,
    OcorrenciaNaoSeAplica,
    ParametrizacaoOcorrencia,
    PeriodoVisita,
    RespostaCampoNumerico,
    RespostaCampoTextoLongo,
    RespostaCampoTextoSimples,
    RespostaDatas,
    RespostaSimNao,
    TipoOcorrencia,
)
from sme_terceirizadas.medicao_inicial.models import SolicitacaoMedicaoInicial


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
    anexos = serializers.JSONField(required=False, allow_null=True)

    def validate(self, attrs):
        if "data" not in attrs:
            raise serializers.ValidationError({"data": ["Este campo é obrigatório!"]})

        return attrs

    def create(self, validated_data):
        usuario = self.context["request"].user
        data_visita = validated_data.pop("data", None)
        ocorrencias_nao_se_aplica = validated_data.pop("ocorrencias_nao_se_aplica", [])
        ocorrencias = validated_data.pop("ocorrencias", [])
        anexos = validated_data.pop("anexos", [])

        form_base = FormularioOcorrenciasBase.objects.create(
            usuario=usuario, data=data_visita
        )

        form_supervisao = FormularioSupervisao.objects.create(
            formulario_base=form_base, **validated_data
        )

        self._create_ocorrencias_nao_se_aplica(ocorrencias_nao_se_aplica, form_base)

        self._create_ocorrencias(ocorrencias, form_base)

        self._create_anexos(form_base, anexos)

        return form_supervisao

    def _create_ocorrencias_nao_se_aplica(self, ocorrencias_data, form_base):
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

    def _create_ocorrencias(self, ocorrencias_data, form_base):
        for ocorrencia_data in ocorrencias_data:
            ocorrencia_data["formulario_base"] = form_base.pk
            parametrizacao_UUID = ocorrencia_data["parametrizacao"]

            try:
                parametrizacao = ParametrizacaoOcorrencia.objects.get(
                    uuid=parametrizacao_UUID
                )
            except ParametrizacaoOcorrencia.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "detail": f"ParametrizacaoOcorrencia com o UUID {parametrizacao_UUID} não foi encontrada"
                    }
                )

            ocorrencia_data["parametrizacao"] = parametrizacao.pk

            response_model_class_name = (
                parametrizacao.tipo_pergunta.get_model_tipo_resposta().__name__
            )
            response_serializer = self.get_serializer_class_by_name(
                f"{response_model_class_name}CreateSerializer"
            )

            serializer = response_serializer(data=ocorrencia_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError(
                    {"parametrizacao": parametrizacao.uuid, "error": serializer.errors}
                )

    def _create_anexos(self, form_base, anexos):
        for anexo in anexos:
            contentfile = convert_base64_to_contentfile(anexo.get("arquivo"))
            AnexosFormularioBase.objects.create(
                formulario_base=form_base,
                anexo=contentfile,
                nome=anexo.get("nome"),
            )

    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)


class FormularioDiretorCreateSerializer(serializers.ModelSerializer):
    data = serializers.DateField(required=True, allow_null=True)
    solicitacao_medicao_inicial = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        allow_null=True,
        queryset=SolicitacaoMedicaoInicial.objects.all(),
    )
    formulario_base = serializers.SlugRelatedField(
        slug_field="uuid",
        required=False,
        allow_null=True,
        queryset=FormularioOcorrenciasBase.objects.all(),
    )
    ocorrencias = serializers.ListField(required=True, allow_null=True)

    def validate(self, attrs):
        if "data" not in attrs:
            raise serializers.ValidationError({"data": ["Este campo é obrigatório!"]})

        return attrs

    def create(self, validated_data):
        usuario = self.context["request"].user
        solicitacao_medicao_inicial = validated_data.pop("solicitacao_medicao_inicial")
        ocorrencias = validated_data.pop("ocorrencias", [])

        form_base = FormularioOcorrenciasBase.objects.create(
            usuario=usuario, data=validated_data.get("data")
        )
        form_diretor = FormularioDiretor.objects.create(
            formulario_base=form_base,
            solicitacao_medicao_inicial=solicitacao_medicao_inicial,
        )
        self._create_ocorrencias(ocorrencias, form_base)

        return form_diretor

    def get_serializer_class_by_name(self, name):
        serializer_class = globals().get(name)
        if serializer_class is None:
            raise ValueError(f"Nenhum serializer encontrado com o nome '{name}'")
        return serializer_class

    def _create_ocorrencias(self, ocorrencias_data, form_base):
        for ocorrencia_data in ocorrencias_data:
            ocorrencia_data_ = copy.deepcopy(ocorrencia_data)
            ocorrencia_data_["formulario_base"] = form_base.pk
            parametrizacao_UUID = ocorrencia_data_["parametrizacao"]

            try:
                parametrizacao = ParametrizacaoOcorrencia.objects.get(
                    uuid=parametrizacao_UUID
                )
            except ParametrizacaoOcorrencia.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "detail": f"ParametrizacaoOcorrencia com o UUID {parametrizacao_UUID} não foi encontrada"
                    }
                )

            ocorrencia_data_["parametrizacao"] = parametrizacao.pk

            response_model_class_name = (
                parametrizacao.tipo_pergunta.get_model_tipo_resposta().__name__
            )
            response_serializer = self.get_serializer_class_by_name(
                f"{response_model_class_name}CreateSerializer"
            )

            serializer = response_serializer(data=ocorrencia_data_)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError(
                    {"parametrizacao": parametrizacao.uuid, "error": serializer.errors}
                )

    class Meta:
        model = FormularioDiretor
        exclude = ("id",)


class FormularioDiretorManyCreateSerializer(serializers.Serializer):
    datas = serializers.ListField(required=True, allow_null=True)
    solicitacao_medicao_inicial = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        allow_null=True,
        queryset=SolicitacaoMedicaoInicial.objects.all(),
    )
    ocorrencias = serializers.ListField(required=True, allow_null=True)

    def create(self, validated_data):
        datas = validated_data.pop("datas")
        validated_data_ = {}
        form_diretor = None

        for data in datas:
            validated_data_["data"] = datetime.datetime.strptime(data, "%d/%m/%Y")
            validated_data_["solicitacao_medicao_inicial"] = validated_data[
                "solicitacao_medicao_inicial"
            ]
            validated_data_["ocorrencias"] = validated_data["ocorrencias"]
            form_serializer = FormularioDiretorCreateSerializer(context=self.context)
            form_diretor = form_serializer.create(validated_data_)

        return form_diretor
