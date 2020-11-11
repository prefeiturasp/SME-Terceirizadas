from rest_framework import serializers

from ...models import SolicitacaoRemessa


class SolicitacaoRemessaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRemessa
        fields = '__all__'
