from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.api.serializers import MealSerializer
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit, OrderMealKit, SolicitacaoUnificadaFormulario, \
    RazaoSolicitacaoUnificada, SolicitacaoUnificadaMultiploEscola, SolicitacaoUnificada
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


class SolicitacaoUnificadaMultiploEscolaSerializer(serializers.ModelSerializer):
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
    kits_lanche = serializers.SerializerMethodField()
    tempo_passeio_formulario = serializers.SerializerMethodField()
    opcao_desejada = serializers.SerializerMethodField()

    def get_escolas(self, obj):
        lote = self.context.get('lote', None)
        if obj.escolas.exists():
            if lote:
                return [{'id': multiplo_escola.escola.eol_code, 'nome': multiplo_escola.escola.name,
                         'numero_alunos': multiplo_escola.numero_alunos, 'check': True} for multiplo_escola in
                        obj.escolas.filter(escola__lote=lote)]
            else:
                return [{'id': multiplo_escola.escola.eol_code, 'nome': multiplo_escola.escola.name,
                         'numero_alunos': multiplo_escola.numero_alunos, 'check': True} for multiplo_escola in
                        obj.escolas.all()]
        else:
            if lote:
                return [{'id': solicitacao.schools.get().eol_code, 'nome': solicitacao.schools.get().name,
                         'nro_alunos': solicitacao.students_quantity, 'tempo_passeio': solicitacao.scheduled_time,
                         'kit_lanche': [kit_lanche.uuid for kit_lanche in solicitacao.meal_kits.all()], 'check': True,
                         'tempo_passeio_formulario': solicitacao.tempo_passeio_formulario,
                         'opcao_desejada': solicitacao.opcao_desejada} for solicitacao in
                        obj.solicitacoes.filter(schools__lote=lote)]
            else:
                return [{'id': solicitacao.schools.get().eol_code, 'nome': solicitacao.schools.get().name,
                         'nro_alunos': solicitacao.students_quantity, 'tempo_passeio': solicitacao.scheduled_time,
                         'kit_lanche': [kit_lanche.uuid for kit_lanche in solicitacao.meal_kits.all()], 'check': True,
                         'tempo_passeio_formulario': solicitacao.tempo_passeio_formulario,
                         'opcao_desejada': solicitacao.opcao_desejada} for solicitacao in obj.solicitacoes.all()]

    def get_razao(self, obj):
        return obj.razao.name

    def get_kit_lanche(self, obj):
        return [kit_lanche.uuid for kit_lanche in obj.kits_lanche.all()]

    def get_kits_lanche(self, obj):
        return {kit_lanche.uuid for kit_lanche in obj.kits_lanche.all()}

    def get_tempo_passeio_formulario(self, obj):
        return obj.tempo_passeio_formulario

    def get_opcao_desejada(self, obj):
        return obj.opcao_desejada

    class Meta:
        model = SolicitacaoUnificadaFormulario
        fields = '__all__'


class SolicitacaoUnificadaSerializer(serializers.ModelSerializer):
    formulario = serializers.SerializerMethodField()
    lote = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    dre = serializers.SerializerMethodField()
    kits_total = serializers.SerializerMethodField()

    def get_formulario(self, obj):
        return SolicitacaoUnificadaFormularioSerializer(obj.formulario, context={'lote': obj.lote}).data

    def get_lote(self, obj):
        return obj.lote.nome

    def get_status(self, obj):
        return obj.status.name

    def get_dre(self, obj):
        return obj.formulario.criado_por.DREs.get().name

    def get_kits_total(self, obj):
        return obj.kits_total

    class Meta:
        model = SolicitacaoUnificada
        fields = '__all__'
