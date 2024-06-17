from rest_framework import serializers
from ...models import Classificacao
from ...constants import CLASSIFICACAO_TIPO
from ....dados_comuns.utils import update_instance_from_dict

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