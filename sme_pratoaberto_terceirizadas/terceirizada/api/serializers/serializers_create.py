from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Lote
from ...models import (Terceirizada)


class TerceirizadaCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(slug_field='uuid', many=True, queryset=Lote.objects.all())

    class Meta:
        model = Terceirizada
        exclude = ('id',)
