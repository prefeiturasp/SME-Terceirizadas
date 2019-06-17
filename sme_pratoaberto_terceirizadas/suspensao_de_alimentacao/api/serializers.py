from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.school.models import SchoolPeriod
from sme_pratoaberto_terceirizadas.suspensao_de_alimentacao.models import SuspensaoDeAlimentacao, \
    StatusSuspensaoDeAlimentacao, DiaRazaoSuspensaoDeAlimentacao, RazaoSuspensaoDeAlimentacao, \
    DescricaoSuspensaoDeAlimentacao
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.validators import nao_pode_ser_passado, deve_pedir_com_antecedencia, dia_util


class RazaoSuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.nome

    def get_value(self, obj):
        return obj.nome

    class Meta:
        model = RazaoSuspensaoDeAlimentacao
        fields = ('label', 'value')


class SuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(slug_field='nome', queryset=StatusSuspensaoDeAlimentacao.objects.all())
    criado_por = serializers.SlugRelatedField(slug_field='uuid', queryset=User.objects.all())
    dias_razoes = serializers.SerializerMethodField()
    descricoes = serializers.SerializerMethodField()

    def get_dias_razoes(self, obj):
        if obj.dias_razoes.exists():
            return DiaRazaoSuspensaoDeAlimentacaoSerializer(obj.dias_razoes.all(), many=True).data
        return None

    def get_descricoes(self, obj):
        if obj.descricoes.exists():
            return DescricaoSuspensaoDeAlimentacaoSerializer(obj.descricoes.all(), many=True).data
        return None


    class Meta:
        model = SuspensaoDeAlimentacao
        fields = '__all__'

    def validate(self, data):
        return data


class DiaRazaoSuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    razao = serializers.SlugRelatedField(slug_field='nome', queryset=RazaoSuspensaoDeAlimentacao.objects.all())
    suspensao_de_alimentacao = serializers.SerializerMethodField()

    def get_suspensao_de_alimentacao(self, obj):
        return obj.suspensao_de_alimentacao.uuid

    class Meta:
        model = DiaRazaoSuspensaoDeAlimentacao
        fields = '__all__'

    def validate_data(self, value):
        if value:
            nao_pode_ser_passado(value)
            deve_pedir_com_antecedencia(value)
        return value

    def validate_data_de(self, value):
        if value:
            nao_pode_ser_passado(value)
            deve_pedir_com_antecedencia(value)
        return value

    def validate_data_ate(self, value):
        if value:
            nao_pode_ser_passado(value)
            deve_pedir_com_antecedencia(value)
        return value

    def validate(self, data):
        if data['data_de'] and data['data_ate'] and data['data_de'] >= data['data_ate']:
            raise serializers.ValidationError('Data inicial não deve ser maior ou igual à data final')
        return data


class DescricaoSuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    periodo = serializers.SlugRelatedField(slug_field='value', queryset=SchoolPeriod.objects.all())
    tipo_de_refeicao = serializers.SlugRelatedField(slug_field='name', queryset=MealType.objects.all(), many=True)
    suspensao_de_alimentacao = serializers.SerializerMethodField()

    def get_suspensao_de_alimentacao(self, obj):
        return obj.suspensao_de_alimentacao.uuid

    class Meta:
        model = DescricaoSuspensaoDeAlimentacao
        fields = '__all__'
