import datetime

from rest_framework import serializers

from ....dados_comuns.api.serializers import (
    LogSolicitacoesUsuarioComVinculoSerializer,
    LogSolicitacoesUsuarioSerializer
)
from ....escola.api.serializers import EscolaSimplissimaSerializer
from ....terceirizada.api.serializers.serializers import TerceirizadaSimplesSerializer
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
    ReclamacaoDeProduto,
    TipoDeInformacaoNutricional,
    LogSolicitacoesUsuario
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


class AnexoReclamacaoDeProdutoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        request = self.context.get('request')
        arquivo = obj.arquivo.url
        return request.build_absolute_uri(arquivo)

    class Meta:
        model = AnexoReclamacaoDeProduto
        fields = ('arquivo', 'nome', 'uuid')


class ImagemDoProdutoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        request = self.context.get('request')
        arquivo = obj.arquivo.url
        return request.build_absolute_uri(arquivo)

    class Meta:
        model = ImagemDoProduto
        fields = ('arquivo', 'nome', 'uuid')


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


class ReclamacaoDeProdutoSerializer(serializers.ModelSerializer):
    escola = EscolaSimplissimaSerializer()
    anexos = serializers.SerializerMethodField()
    status_titulo = serializers.CharField(source='status.state.title')
    logs = serializers.SerializerMethodField()

    def get_anexos(self, obj):
        return AnexoReclamacaoDeProdutoSerializer(
            obj.anexos.all(),
            context=self.context,
            many=True
        ).data

    def get_logs(self, obj):
        return LogSolicitacoesUsuarioSerializer(
            LogSolicitacoesUsuario.objects.filter(uuid_original=obj.uuid),
            many=True).data

    class Meta:
        model = ReclamacaoDeProduto
        fields = ('uuid', 'reclamante_registro_funcional', 'logs', 'reclamante_cargo', 'reclamante_nome',
                  'reclamacao', 'escola', 'anexos', 'status', 'status_titulo', 'criado_em')


class ReclamacaoDeProdutoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReclamacaoDeProduto
        fields = ('reclamacao', 'criado_em')


class HomologacaoProdutoSimplesSerializer(serializers.ModelSerializer):
    reclamacoes = serializers.SerializerMethodField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    logs = LogSolicitacoesUsuarioComVinculoSerializer(many=True)

    def get_reclamacoes(self, obj):
        return ReclamacaoDeProdutoSerializer(
            obj.reclamacoes.all(), context=self.context,
            many=True
        ).data

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'status', 'id_externo', 'rastro_terceirizada', 'logs',
                  'criado_em', 'reclamacoes')


class ProdutoSerializer(serializers.ModelSerializer):
    protocolos = ProtocoloDeDietaEspecialSerializer(many=True)
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    imagens = serializers.ListField(
        child=ImagemDoProdutoSerializer(), required=True
    )
    id_externo = serializers.CharField()

    informacoes_nutricionais = serializers.SerializerMethodField()

    homologacoes = serializers.SerializerMethodField()

    ultima_homologacao = HomologacaoProdutoSimplesSerializer()

    def get_homologacoes(self, obj):
        return HomologacaoProdutoSimplesSerializer(
            HomologacaoDoProduto.objects.filter(
                produto=obj
            ), context=self.context,
            many=True
        ).data

    def get_informacoes_nutricionais(self, obj):
        return InformacoesNutricionaisDoProdutoSerializer(
            InformacoesNutricionaisDoProduto.objects.filter(
                produto=obj
            ), many=True
        ).data

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
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'produto', 'status', 'id_externo', 'logs', 'rastro_terceirizada', 'pdf_gerado',
                  'protocolo_analise_sensorial')


class HomologacaoProdutoPainelGerencialSerializer(serializers.ModelSerializer):
    nome_produto = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    def get_nome_produto(self, obj):
        return obj.produto.nome

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'nome_produto', 'status', 'id_externo', 'log_mais_recente')
