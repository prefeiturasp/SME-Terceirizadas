from rest_framework import serializers

from sme_terceirizadas.imr.models import (FormularioSupervisao, PeriodoVisita, TipoOcorrencia, CategoriaOcorrencia,
                                          ParametrizacaoOcorrencia, TipoPerguntaParametrizacaoOcorrencia, TipoPenalidade)


class PeriodoVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoVisita
        exclude = ("id",)


class FormularioSupervisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioSupervisao
        exclude = ("id",)


class CategoriaOcorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaOcorrencia
        fields = ("uuid", "nome", "posicao", )


class TipoPerguntaParametrizacaoOcorrenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoPerguntaParametrizacaoOcorrencia
        fields = ("uuid", "nome", )


class ParametrizacaoOcorrenciaSerializer(serializers.ModelSerializer):
    tipo_pergunta = TipoPerguntaParametrizacaoOcorrenciaSerializer()

    class Meta:
        model = ParametrizacaoOcorrencia
        fields = ("uuid", "posicao", "titulo", "tipo_pergunta", )


class TipoPenalidadeSerializer(serializers.ModelSerializer):
    obrigacoes = serializers.SerializerMethodField()

    class Meta:
        model = TipoPenalidade
        fields = ("uuid", "numero_clausula", "descricao", "obrigacoes", )

    def get_obrigacoes(self, obj):
        obrigacoes = obj.obrigacoes.all()
        return [obrigacao.descricao for obrigacao in obrigacoes]


class TipoOcorrenciaSerializer(serializers.ModelSerializer):
    categoria = CategoriaOcorrenciaSerializer()
    parametrizacoes = ParametrizacaoOcorrenciaSerializer(many=True)
    penalidade = TipoPenalidadeSerializer()

    class Meta:
        model = TipoOcorrencia
        fields = ("uuid", "titulo", "descricao", "posicao", "categoria", "parametrizacoes", "penalidade", )
