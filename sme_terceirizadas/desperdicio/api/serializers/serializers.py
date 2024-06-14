from rest_framework import serializers
from ...models import Classificacao

class ClassificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classificacao
        exclude = ('id',)


class ClassificacaoCreateSerializer(serializers.Serializer):
    tipo = serializers.CharField(required=True)
    descricao = serializers.CharField(required=True)
    valor = serializers.CharField(required=True)
    
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