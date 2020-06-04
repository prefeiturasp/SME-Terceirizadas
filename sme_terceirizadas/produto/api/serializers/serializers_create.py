from rest_framework import serializers

from ....dados_comuns.constants import DEZ_MB
from ....dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from ...models import (
    AnexoReclamacaoDeProduto,
    Fabricante,
    HomologacaoDoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
    ReclamacaoDeProduto
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
    cadastro_finalizado = serializers.BooleanField(required=False)
    cadastro_atualizado = serializers.BooleanField(required=False)

    def create(self, validated_data):  # noqa C901
        validated_data['criado_por'] = self.context['request'].user
        imagens = validated_data.pop('imagens', [])
        protocolos = validated_data.pop('protocolos', [])
        informacoes_nutricionais = validated_data.pop('informacoes_nutricionais', [])
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', False)

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
        if produto.homologacoes.exists():
            homologacao = produto.homologacoes.first()
        else:
            homologacao = HomologacaoDoProduto(
                rastro_terceirizada=self.context['request'].user.vinculo_atual.instituicao,
                produto=produto,
                criado_por=self.context['request'].user
            )
            homologacao.save()
        if cadastro_finalizado:
            homologacao.inicia_fluxo(user=self.context['request'].user)
        return produto

    def update(self, instance, validated_data): # noqa C901
        imagens = validated_data.pop('imagens', [])
        protocolos = validated_data.pop('protocolos', [])
        informacoes_nutricionais = validated_data.pop('informacoes_nutricionais', [])

        update_instance_from_dict(instance, validated_data, save=True)

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
        usuario = self.context['request'].user
        if validated_data.get('cadastro_atualizado', False):
            ultima_homologacao = instance.homologacoes.first()
            ultima_homologacao.inativa_homologacao(user=usuario)
            homologacao = HomologacaoDoProduto(
                rastro_terceirizada=usuario.vinculo_atual.instituicao,
                produto=instance,
                criado_por=usuario
            )
            homologacao.save()
            homologacao.inicia_fluxo(user=usuario)
        if validated_data.get('cadastro_finalizado', False):
            homologacao = instance.homologacoes.first()
            homologacao.inicia_fluxo(user=usuario)
        return instance

    class Meta:
        model = Produto
        exclude = ('id', 'criado_por', 'ativo',)


class AnexoReclamacaoDeProdutoCreateSerializer(serializers.Serializer):
    base64 = serializers.CharField(max_length=DEZ_MB, write_only=True)
    nome = serializers.CharField(max_length=255)


class ReclamacaoDeProdutoSerializerCreate(serializers.ModelSerializer):
    anexos = AnexoReclamacaoDeProdutoCreateSerializer(many=True)

    def create(self, validated_data):  # noqa C901
        anexos = validated_data.pop('anexos', [])

        reclamacao = ReclamacaoDeProduto.objects.create(**validated_data)

        for anexo in anexos:
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoReclamacaoDeProduto.objects.create(
                reclamacao_de_produto=reclamacao,
                arquivo=arquivo,
                nome=anexo['nome']
            )

        return reclamacao

    class Meta:
        model = ReclamacaoDeProduto
        exclude = ('id', 'uuid', 'criado_por', 'criado_em')
