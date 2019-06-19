from rest_framework import serializers
from ..models import Permissao


class PermissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissao
        fields = ['titulo', 'uuid']
