from rest_framework import serializers

from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    Equipamento,
    FormularioSupervisao,
    Insumo,
    Mobiliario,
    ParametrizacaoOcorrencia,
    PeriodoVisita,
    ReparoEAdaptacao,
    TipoOcorrencia,
    TipoPenalidade,
    TipoPerguntaParametrizacaoOcorrencia,
    UtensilioCozinha,
    UtensilioMesa,
)


class PeriodoVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoVisita
        exclude = ("id",)


class FormularioSupervisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)


class FormularioSupervisaoSimplesSerializer(serializers.ModelSerializer):
    diretoria_regional = serializers.CharField(source="escola.diretoria_regional.nome")
    unidade_educacional = serializers.CharField(source="escola.nome")
    data = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    def get_data(self, obj):
        return obj.formulario_base.data.strftime("%d/%m/%Y")

    class Meta:
        model = FormularioSupervisao
        fields = (
            "uuid",
            "diretoria_regional",
            "unidade_educacional",
            "data",
            "status",
        )


class CategoriaOcorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaOcorrencia
        fields = (
            "uuid",
            "nome",
            "posicao",
            "gera_notificacao",
        )


class TipoPerguntaParametrizacaoOcorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPerguntaParametrizacaoOcorrencia
        fields = (
            "uuid",
            "nome",
        )


class ParametrizacaoOcorrenciaSerializer(serializers.ModelSerializer):
    tipo_pergunta = TipoPerguntaParametrizacaoOcorrenciaSerializer()

    class Meta:
        model = ParametrizacaoOcorrencia
        fields = (
            "uuid",
            "posicao",
            "titulo",
            "tipo_pergunta",
        )


class TipoPenalidadeSerializer(serializers.ModelSerializer):
    obrigacoes = serializers.SerializerMethodField()

    class Meta:
        model = TipoPenalidade
        fields = (
            "uuid",
            "numero_clausula",
            "descricao",
            "obrigacoes",
        )

    def get_obrigacoes(self, obj):
        obrigacoes = obj.obrigacoes.all()
        return [obrigacao.descricao for obrigacao in obrigacoes]


class TipoOcorrenciaSerializer(serializers.ModelSerializer):
    categoria = CategoriaOcorrenciaSerializer()
    parametrizacoes = ParametrizacaoOcorrenciaSerializer(many=True)
    penalidade = TipoPenalidadeSerializer()

    class Meta:
        model = TipoOcorrencia
        fields = (
            "uuid",
            "titulo",
            "descricao",
            "posicao",
            "categoria",
            "parametrizacoes",
            "penalidade",
            "aceita_multiplas_respostas",
        )


class UtensilioCozinhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtensilioCozinha
        exclude = ("id",)


class UtensilioMesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtensilioMesa
        exclude = ("id",)


class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        exclude = ("id",)


class MobiliarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobiliario
        exclude = ("id",)


class ReparoEAdaptacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReparoEAdaptacao
        exclude = ("id",)


class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        exclude = ("id",)
