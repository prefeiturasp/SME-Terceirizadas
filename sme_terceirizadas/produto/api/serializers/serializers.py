from rest_framework import serializers

from ....terceirizada.api.serializers.serializers import TerceirizadaSimplesSerializer
from ...models import (
    Fabricante,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
    TipoDeInformacaoNutricional, HomologacaoDoProduto
)


class FabricanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        exclude = ('id',)


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        exclude = ('id',)


class ProtocoloDeDietaEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloDeDietaEspecial
        exclude = ('id', 'ativo', 'criado_em', 'criado_por',)


class ImagemDoProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemDoProduto
        fields = ('arquivo', 'nome')


class TipoDeInformacaoNutricionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDeInformacaoNutricional
        exclude = ('id',)


class InformacaoNutricionalSerializer(serializers.ModelSerializer):
    tipo_nutricional = TipoDeInformacaoNutricionalSerializer()

    class Meta:
        model = InformacaoNutricional
        exclude = ('id',)


class InformacoesNutricionaisDoProdutoSerializer(serializers.ModelSerializer):
    informacao_nutricional = InformacaoNutricionalSerializer()

    class Meta:
        model = InformacoesNutricionaisDoProduto
        exclude = ('id', 'produto')


class ProdutoSerializer(serializers.ModelSerializer):
    protocolos = ProtocoloDeDietaEspecialSerializer(many=True)
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    imagens = serializers.ListField(
        child=ImagemDoProdutoSerializer(), required=True
    )

    informacoes_nutricionais = serializers.SerializerMethodField()
    terceirizada = serializers.SerializerMethodField()

    def get_informacoes_nutricionais(self, obj):
        return InformacoesNutricionaisDoProdutoSerializer(
            InformacoesNutricionaisDoProduto.objects.filter(
                produto=obj
            ), many=True
        ).data

    def get_terceirizada(self, obj):
        return TerceirizadaSimplesSerializer(obj.criado_por.vinculo_atual.instituicao).data

    class Meta:
        model = Produto
        exclude = ('id',)


class ProdutoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ('uuid', 'nome',)


class MarcaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ('uuid', 'nome',)


class FabricanteSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        fields = ('uuid', 'nome',)


class ProtocoloSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloDeDietaEspecial
        fields = ('uuid', 'nome',)


class HomologacaoProdutoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer()

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'produto', 'status', 'id_externo')
