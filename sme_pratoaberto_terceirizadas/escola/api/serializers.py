from rest_framework import serializers

from ..models import (Escola, PeriodoEscolar, DiretoriaRegional,
                      FaixaIdadeEscolar, TipoUnidadeEscolar, TipoGestao, )
from ...terceirizada.api.serializers import LoteSerializer


class PeriodoEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoEscolar
        exclude = ('id',)


class TipoGestaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGestao
        exclude = ('id',)


class TipoUnidadeEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUnidadeEscolar
        exclude = ('id',)


class FaixaIdadeEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaixaIdadeEscolar
        exclude = ('id',)


class DiretoriaRegionalSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        exclude = ('id',)


class EscolaCompletaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplesSerializer()
    idades = FaixaIdadeEscolarSerializer(many=True)
    tipo_unidade = TipoUnidadeEscolarSerializer()
    tipo_gestao = TipoGestaoSerializer()
    periodos = PeriodoEscolarSerializer(many=True)
    lote = LoteSerializer()

    class Meta:
        model = Escola
        exclude = ('cardapios', 'id')


class EscolaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'quantidade_alunos')


class DiretoriaRegionalCompletaSerializer(serializers.ModelSerializer):
    lotes = LoteSerializer(many=True)
    escolas = EscolaSimplesSerializer(many=True)

    class Meta:
        model = DiretoriaRegional
        exclude = ('id',)
