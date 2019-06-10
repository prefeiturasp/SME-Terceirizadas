from rest_framework import serializers

from sme_pratoaberto_terceirizadas.suspensao_de_alimentacao.models import SuspensaoDeAlimentacao, \
    StatusSuspensaoDeAlimentacao, DiaRazaoSuspensaoDeAlimentacao, RazaoSuspensaoDeAlimentacao
from sme_pratoaberto_terceirizadas.users.models import User


class SuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(slug_field='nome', queryset=StatusSuspensaoDeAlimentacao.objects.all())
    criado_por = serializers.SlugRelatedField(slug_field='uuid', queryset=User.objects.all())

    class Meta:
        model = SuspensaoDeAlimentacao
        fields = '__all__'

    def validate(self, data):
        return data


class DiaRazaoSuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    razao = serializers.SlugRelatedField(slug_field='nome', queryset=RazaoSuspensaoDeAlimentacao.objects.all())
    suspensao_de_alimentacao = serializers.SerializerMethodField()

    class Meta:
        model = DiaRazaoSuspensaoDeAlimentacao
        fields = '__all__'

    def validate_suspensao_de_alimentacao(self, value):
        print('validate')
        return value
