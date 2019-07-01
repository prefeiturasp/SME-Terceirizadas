from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimento.models import TipoRefeicao
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar
from sme_pratoaberto_terceirizadas.suspensao_de_alimentacao.models import SuspensaoDeAlimentacao, \
    StatusSuspensaoDeAlimentacao, DiaRazaoSuspensaoDeAlimentacao, RazaoSuspensaoDeAlimentacao, \
    DescricaoSuspensaoDeAlimentacao
from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from sme_pratoaberto_terceirizadas.validators import nao_pode_ser_passado, deve_pedir_com_antecedencia, dia_util


class SuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(slug_field='nome', queryset=StatusSuspensaoDeAlimentacao.objects.all())
    criado_por = serializers.SlugRelatedField(slug_field='uuid', queryset=Usuario.objects.all())

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

    def validate_data(self, value):
        nao_pode_ser_passado(value)
        deve_pedir_com_antecedencia(value)
        dia_util(value)
        return value

    def validate_data_de(self, value):
        nao_pode_ser_passado(value)
        deve_pedir_com_antecedencia(value)
        dia_util(value)
        return value

    def validate_data_ate(self, value):
        nao_pode_ser_passado(value)
        deve_pedir_com_antecedencia(value)
        dia_util(value)
        return value

    def validate(self, data):
        if data['data_de'] and data['data_ate'] and data['data_de'] >= data['data_ate']:
            raise serializers.ValidationError('Data inicial não deve ser maior ou igual à data final')
        return data


class DescricaoSuspensaoDeAlimentacaoSerializer(serializers.ModelSerializer):
    periodo = serializers.SlugRelatedField(slug_field='value', queryset=PeriodoEscolar.objects.all())
    tipo_de_refeicao = serializers.SlugRelatedField(slug_field='name', queryset=TipoRefeicao.objects.all(), many=True)
    suspensao_de_alimentacao = serializers.SerializerMethodField()

    class Meta:
        model = DescricaoSuspensaoDeAlimentacao
        fields = '__all__'
