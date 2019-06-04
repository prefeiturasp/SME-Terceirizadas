from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.api.serializers import MealSerializer
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit, OrderMealKit, SolicitacaoUnificadaFormulario, \
    RazaoSolicitacaoUnificada, SolicitacaoUnificadaMultiploEscola
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer


class MealKitSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = MealKit
        fields = ['uuid', 'name', 'is_active', 'meals']


class OrderMealKitSerializer(serializers.ModelSerializer):
    schools = SchoolSerializer(many=True, read_only=True)
    meal_kits = MealKitSerializer(many=True, read_only=True)

    class Meta:
        model = OrderMealKit
        fields = '__all__'


class SolicitacaoUnificadaMultiploEscolaSerializer(serializers.SerializerMethodField):
    class Meta:
        model = SolicitacaoUnificadaMultiploEscola
        fields = '__all__'


class RazaoSolicitacaoUnificadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RazaoSolicitacaoUnificada
        fields = ('name',)


class SolicitacaoUnificadaFormularioSerializer(serializers.ModelSerializer):
    escolas = serializers.SerializerMethodField()
    razao = serializers.SerializerMethodField()
    kit_lanche = serializers.SerializerMethodField()

    def get_escolas(self, obj):
        if obj.escolas.exists():
            return [{'id': multiplo_escola.escola.eol_code, 'nome': multiplo_escola.escola.name,
                     'numero_alunos': multiplo_escola.numero_alunos, 'check': True} for multiplo_escola in
                    obj.escolas.all()]
        else:
            return [{'id': solicitacao.schools.get().eol_code, 'nome': solicitacao.schools.get().name,
                     'nro_alunos': solicitacao.students_quantity, 'tempo_passeio': solicitacao.scheduled_time,
                     'kit_lanche': [kit_lanche.uuid for kit_lanche in solicitacao.meal_kits.all()], 'check': True} for
                    solicitacao in obj.solicitacoes.all()]

    def get_razao(self, obj):
        return obj.razao.name

    def get_kit_lanche(self, obj):
        return [kit_lanche.uuid for kit_lanche in obj.kits_lanche.all()]

    class Meta:
        model = SolicitacaoUnificadaFormulario
        fields = '__all__'
