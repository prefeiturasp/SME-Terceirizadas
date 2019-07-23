from rest_framework import serializers

from ..models import (Edital)


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)
