from rest_framework import serializers

from ..models import Escola, PeriodoEscolar, DiretoriaRegional, FaixaIdadeEscolar


# from sme_pratoaberto_terceirizadas.alimento.api.serializers import TipoRefeicaoSerializer

class FaixaIdadeEscolarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FaixaIdadeEscolar
        exclude = ('id',)


class DiretoriaRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        # exclude = ('id',)
        include = '__all__'


class EscolaSerializer(serializers.ModelSerializer):
    # diretoria_regional = DiretoriaRegionalSerializer()
    # idades = FaixaIdadeEscolarSerializer()
    # idades = serializers.RelatedField(read_only=True)
    # idades = FaixaIdadeEscolarSerializer()

    class Meta:
        model = Escola
        exclude = ('cardapios', 'id')
        depth = 1


class PeriodoEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoEscolar
        exclude = ('id',)
