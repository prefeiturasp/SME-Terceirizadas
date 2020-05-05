from rest_framework import serializers

from ....dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from ...models import (
    Fabricante,
    HomologacaoDoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial
)
from ..validators import deve_ter_extensao_valida


class ImagemDoProdutoSerializerCreate(serializers.ModelSerializer):
    arquivo = serializers.CharField()
    nome = serializers.CharField()

    def validate_nome(self, nome):
        deve_ter_extensao_valida(nome)
        return nome

    class Meta:
        model = ImagemDoProduto
        exclude = ('id', 'produto',)


class InformacoesNutricionaisDoProdutoSerializerCreate(serializers.ModelSerializer):
    informacao_nutricional = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=InformacaoNutricional.objects.all()
    )

    quantidade_porcao = serializers.CharField(required=True)
    valor_diario = serializers.CharField(required=True)

    class Meta:
        model = InformacoesNutricionaisDoProduto
        exclude = ('id', 'produto',)


class ProdutoSerializerCreate(serializers.ModelSerializer):
    protocolos = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=ProtocoloDeDietaEspecial.objects.all(),
        many=True
    )
    marca = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Marca.objects.all()
    )
    fabricante = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Fabricante.objects.all()
    )

    imagens = ImagemDoProdutoSerializerCreate(many=True)
    informacoes_nutricionais = InformacoesNutricionaisDoProdutoSerializerCreate(many=True)

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        imagens = validated_data.pop('imagens', [])
        protocolos = validated_data.pop('protocolos', [])
        informacoes_nutricionais = validated_data.pop('informacoes_nutricionais', [])

        produto = Produto.objects.create(**validated_data)

        for imagem in imagens:
            data = convert_base64_to_contentfile(imagem.get('arquivo'))
            ImagemDoProduto.objects.create(
                produto=produto, arquivo=data, nome=imagem.get('nome', '')
            )

        for informacao in informacoes_nutricionais:
            InformacoesNutricionaisDoProduto.objects.create(
                produto=produto,
                informacao_nutricional=informacao.get('informacao_nutricional', ''),
                quantidade_porcao=informacao.get('quantidade_porcao', ''),
                valor_diario=informacao.get('valor_diario', '')
            )

        produto.protocolos.set(protocolos)
        homologacao = HomologacaoDoProduto(
            produto=produto,
            criado_por=self.context['request'].user
        )
        homologacao.save()
        if validated_data.get('cadastro_finalizado', False):
            homologacao.inicia_fluxo(user=self.context['request'].user)
        return produto

    def update(self, instance, validated_data):
        imagens = validated_data.pop('imagens', [])
        protocolos = validated_data.pop('protocolos', [])
        informacoes_nutricionais = validated_data.pop('informacoes_nutricionais', [])

        update_instance_from_dict(instance, validated_data, save=True)

        instance.imagens.all().delete()
        instance.informacoes_nutricionais.all().delete()

        for imagem in imagens:
            data = convert_base64_to_contentfile(imagem.get('arquivo'))
            ImagemDoProduto.objects.create(
                produto=instance, arquivo=data, nome=imagem.get('nome', '')
            )

        for informacao in informacoes_nutricionais:
            InformacoesNutricionaisDoProduto.objects.create(
                produto=instance,
                informacao_nutricional=informacao.get('informacao_nutricional', ''),
                quantidade_porcao=informacao.get('quantidade_porcao', ''),
                valor_diario=informacao.get('valor_diario', '')
            )

        instance.protocolos.set([])
        instance.protocolos.set(protocolos)
        return instance

    class Meta:
        model = Produto
        exclude = ('id', 'criado_por', 'ativo',)
