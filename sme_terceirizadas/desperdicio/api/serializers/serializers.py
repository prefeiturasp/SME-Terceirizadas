import environ

from rest_framework import serializers
from ....perfil.api.serializers import UsuarioVinculoSerializer
from ....dados_comuns.utils import update_instance_from_dict
from ....dados_comuns.utils import convert_base64_to_contentfile
from ....dados_comuns.validators import deve_ter_extensao_valida

from ...models import (
    Classificacao,
    ControleSobras,
    ControleRestos,
    ImagemControleResto,
)
from ....escola.models import Escola
from ....produto.models import TipoAlimento, TipoRecipiente
from ....escola.api.serializers import EscolaSimplesSerializer
from ....cardapio.models import TipoAlimentacao

from ...constants import CLASSIFICACAO_TIPO, DESPERDICIO_PERIODO
from ...constants import DESPERDICIO_PERIODO

class ControleSobrasSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    usuario = UsuarioVinculoSerializer()
    tipo_alimentacao_nome = serializers.SerializerMethodField()
    tipo_alimento_nome = serializers.SerializerMethodField()
    tipo_recipiente_nome = serializers.SerializerMethodField()

    def get_tipo_alimentacao_nome(self, obj):
        return obj.tipo_alimentacao.nome

    def get_tipo_alimento_nome(self, obj):
        return obj.tipo_alimento.nome

    def get_tipo_recipiente_nome(self, obj):
        return obj.tipo_recipiente.nome

    class Meta:
        model = ControleSobras
        exclude = ('id',)


class ControleSobrasCreateSerializer(serializers.Serializer):
    escola = serializers.CharField(required=True)
    tipo_alimentacao = serializers.CharField(required=True)
    tipo_alimento = serializers.CharField(required=True)
    peso_alimento = serializers.CharField(required=True)
    tipo_recipiente = serializers.CharField(required=True)
    peso_recipiente = serializers.CharField(required=True)
    peso_sobra = serializers.CharField(required=True)
    data_medicao = serializers.DateField(required=True)
    periodo = serializers.CharField(required=True)

    def validate(self, attrs):
        periodo = attrs['periodo']

        if periodo not in DESPERDICIO_PERIODO:
            raise serializers.ValidationError('Período inválido.')
        
        return attrs

    def create(self, validated_data):
        escola = Escola.objects.get(uuid=validated_data['escola'])
        tipo_alimentacao = TipoAlimentacao.objects.get(uuid=validated_data['tipo_alimentacao'])
        tipo_alimento = TipoAlimento.objects.get(uuid=validated_data['tipo_alimento'])
        peso_alimento = validated_data['peso_alimento']
        tipo_recipiente = TipoRecipiente.objects.get(uuid=validated_data['tipo_recipiente'])
        peso_recipiente = validated_data['peso_recipiente']
        peso_sobra = validated_data['peso_sobra']
        usuario = self.context['request'].user
        data_medicao = validated_data['data_medicao']
        periodo = validated_data['periodo']

        try:
            item = ControleSobras.objects.create(
                escola=escola,
                tipo_alimentacao=tipo_alimentacao,
                tipo_alimento=tipo_alimento,
                peso_alimento=peso_alimento,
                tipo_recipiente=tipo_recipiente,
                peso_recipiente=peso_recipiente,
                peso_sobra=peso_sobra,
                usuario=usuario,
                data_medicao=data_medicao,
                periodo=periodo
            )
            return item
        except Exception as e:
            print(e)
            raise serializers.ValidationError('Erro ao criar ControleSobras.')


class ImagemControleRestoCreateSerializer(serializers.ModelSerializer):
    arquivo = serializers.CharField()
    nome = serializers.CharField()

    def validate_nome(self, nome):
        deve_ter_extensao_valida(nome)
        return nome

    class Meta:
        model = ImagemControleResto
        fields = ('arquivo', 'nome')


class ImagemControleRestoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{obj.arquivo.url}'

    class Meta:
        model = ImagemControleResto
        fields = ('arquivo', 'nome')


class ControleRestosSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    usuario = UsuarioVinculoSerializer()
    tipo_alimentacao_nome = serializers.SerializerMethodField()
    imagens = serializers.ListField(
        child=ImagemControleRestoSerializer(), required=True
    )

    def get_tipo_alimentacao_nome(self, obj):
        return obj.tipo_alimentacao.nome

    class Meta:
        model = ControleRestos
        exclude = ('id',)


class ControleRestosCreateSerializer(serializers.Serializer):
    escola = serializers.CharField(required=True)
    tipo_alimentacao = serializers.CharField(required=True)
    peso_resto = serializers.CharField(required=True)
    cardapio = serializers.CharField(required=True)
    resto_predominante = serializers.CharField(required=True)
    quantidade_distribuida = serializers.CharField(required=True)
    data_medicao = serializers.DateField(required=True)
    periodo = serializers.CharField(required=True)
    imagens = serializers.ListField(
        required=False,
        child=ImagemControleRestoCreateSerializer()
    )

    def validate(self, attrs):
        periodo = attrs['periodo']

        if periodo not in DESPERDICIO_PERIODO:
            raise serializers.ValidationError('Período inválido.')
        
        return attrs

    def create(self, validated_data):
        escola = Escola.objects.get(uuid=validated_data['escola'])
        tipo_alimentacao = TipoAlimentacao.objects.get(uuid=validated_data['tipo_alimentacao'])
        peso_resto = validated_data['peso_resto']
        cardapio = validated_data['cardapio']
        resto_predominante = validated_data['resto_predominante']
        usuario = self.context['request'].user
        imagens = validated_data.pop('imagens', [])
        quantidade_distribuida = validated_data['quantidade_distribuida']
        data_medicao = validated_data['data_medicao']
        periodo = validated_data['periodo']

        try:
            item = ControleRestos.objects.create(
                escola=escola,
                tipo_alimentacao=tipo_alimentacao,
                peso_resto=peso_resto,
                cardapio=cardapio,
                resto_predominante=resto_predominante,
                usuario=usuario,
                data_medicao=data_medicao,
                periodo=periodo,
                quantidade_distribuida=quantidade_distribuida
            )

            for imagem in imagens:
                data = convert_base64_to_contentfile(imagem.get('arquivo'))
                ImagemControleResto.objects.create(
                    controle_resto=item,
                    arquivo=data,
                    nome=imagem.get('nome', '')
                )

            return item
        except Exception as e:
            print(e)
            raise serializers.ValidationError('Erro ao criar ControleRestos.')

def format_periodo(value):
    if (value is None):
        return None
    
    if value == 'M':
        return 'Manhã'
    if value == 'T':
        return 'Tarde'
    if value == 'I':
        return 'Integral'

    return value

def serialize_relatorio_controle_restos(row):
    data_medicao, periodo, dre_nome, escola_nome, quantidade_distribuida_soma, peso_resto_soma, num_refeicoes, resto_per_capita, percent_resto, classificacao = row

    def format_float(value):
        if (value is None):
            return None
        
        return "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")

    def format_int(value):
        if (value is None):
            return None

        return int(value)

    return {
        'dre_nome': dre_nome,
        'escola_nome': escola_nome,
        'data_medicao': data_medicao.strftime('%d/%m/%Y') if data_medicao else None,
        'periodo': format_periodo(periodo),
        'quantidade_distribuida_soma': format_float(quantidade_distribuida_soma),
        'peso_resto_soma': format_float(peso_resto_soma),
        'num_refeicoes': format_int(num_refeicoes),
        'resto_per_capita': format_float(resto_per_capita),
        'percent_resto': format_float(percent_resto),
        'classificacao': classificacao
    }


def serialize_relatorio_controle_sobras(row):

    data_medicao, periodo, dre_nome, escola_nome, tipo_alimentacao_nome, tipo_alimento_nome, peso_alimento, peso_sobra, quantidade_distribuida, frequencia, total_primeira_oferta, total_repeticao, percentual_sobra, media_por_aluno, media_por_refeicao, classificacao = row

    def format_float(value):
        if (value is None):
            return None
        
        return "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
    
    def format_int(value):
        if (value is None):
            return None

        return int(value)

    return {
        'dre_nome': dre_nome,
        'escola_nome': escola_nome,
        'tipo_alimentacao_nome': tipo_alimentacao_nome,
        'tipo_alimento_nome': tipo_alimento_nome,
        'data_medicao': data_medicao.strftime('%d/%m/%Y') if data_medicao else None,
        'periodo': format_periodo(periodo),
        'peso_alimento': format_float(peso_alimento),
        'peso_sobra': format_float(peso_sobra),
        'quantidade_distribuida': format_float(quantidade_distribuida),
        'frequencia': format_int(frequencia),
        'total_primeira_oferta': format_int(total_primeira_oferta),
        'total_repeticao': format_int(total_repeticao),
        'percentual_sobra': format_float(percentual_sobra),
        'media_por_aluno': format_float(media_por_aluno),
        'media_por_refeicao': format_float(media_por_refeicao),
        'classificacao': classificacao
    }


class ClassificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classificacao
        exclude = ('id',)


class ClassificacaoCreateSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=False)
    tipo = serializers.CharField(required=True)
    descricao = serializers.CharField(required=True)
    valor = serializers.CharField(required=True)
    
    def validate(self, attrs):
        tipo = attrs['tipo']
        valor = attrs['valor']
        
        if tipo not in CLASSIFICACAO_TIPO:
            raise serializers.ValidationError('Tipo de Classificação inválido.')
        
        if attrs.get('uuid'):
            queryset = Classificacao.objects.exclude(uuid=attrs['uuid']).filter(tipo=tipo, valor=valor)
        else:
            queryset = Classificacao.objects.filter(tipo=tipo, valor=valor)
        if queryset.exists():
            raise serializers.ValidationError('Já existe uma classificação com esse tipo e valor.')
        
        attrs.pop('uuid', None)
        return attrs
    
    def create(self, validated_data):
        tipo = validated_data['tipo']
        descricao = validated_data['descricao']
        valor = validated_data['valor']
        
        try:
            item = Classificacao.objects.create(
                tipo=tipo,
                descricao=descricao,
                valor=valor
            )

            return item
        except Exception as e:
            print(e)
            raise serializers.ValidationError('Erro ao criar Classificação.')
        
    def update(self, instance, validated_data):
        update_instance_from_dict(instance, validated_data, save=True)
        return instance