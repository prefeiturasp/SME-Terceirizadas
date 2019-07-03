from rest_framework import serializers

from ..models import (Escola, PeriodoEscolar, DiretoriaRegional,
                      FaixaIdadeEscolar, TipoUnidadeEscolar, TipoGestao, )
from ...terceirizada.api.serializers import LoteSerializer


# from sme_pratoaberto_terceirizadas.alimento.api.serializers import TipoRefeicaoSerializer

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


class DiretoriaRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        # exclude = ('id',)
        fields = '__all__'


class EscolaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSerializer()
    idades = FaixaIdadeEscolarSerializer(many=True)
    tipo_unidade = TipoUnidadeEscolarSerializer()
    tipo_gestao = TipoGestaoSerializer()
    periodos = PeriodoEscolarSerializer(many=True)
    lote = LoteSerializer()

    class Meta:
        model = Escola
        exclude = ('cardapios', 'id')
        # depth = 1
