from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food_inclusion.models import InclusaoAlimentacao, DescricaoInclusaoAlimentacao, \
    MotivoInclusaoAlimentacao, DiaMotivoInclusaoAlimentacao
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar


class FoodInclusionReasonSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.name

    class Meta:
        model = MotivoInclusaoAlimentacao
        fields = ('label', 'value')


class FoodInclusionDayReasonSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    date_from = serializers.SerializerMethodField()
    date_to = serializers.SerializerMethodField()
    weekdays = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()

    def get_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else None

    def get_date_from(self, obj):
        return obj.date_from.strftime('%d/%m/%Y') if obj.date_from else None

    def get_date_to(self, obj):
        return obj.date_to.strftime('%d/%m/%Y') if obj.date_to else None

    def get_weekdays(self, obj):
        if obj.weekdays:
            if isinstance(obj.weekdays, list):
                return obj.weekdays
            else:
                return [day for day in obj.weekdays.split(',')]
        return None

    def get_reason(self, obj):
        return obj.reason.name

    class Meta:
        model = DiaMotivoInclusaoAlimentacao
        fields = ('id', 'date', 'date_from', 'date_to', 'weekdays', 'which_reason', 'priority', 'reason')


class FoodInclusionDescriptionSerializer(serializers.ModelSerializer):
    check = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    select = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()

    def get_check(self, obj):
        return True

    def get_value(self, obj):
        return obj.period.value

    def get_select(self, obj):
        return [meal.name for meal in obj.meal_type.all()]

    def get_number(self, obj):
        return str(obj.number_of_students)

    class Meta:
        model = DescricaoInclusaoAlimentacao
        fields = ('check', 'value', 'select', 'number')


class FoodInclusionSerializer(serializers.ModelSerializer):
    description_first_period = serializers.SerializerMethodField()
    description_second_period = serializers.SerializerMethodField()
    description_third_period = serializers.SerializerMethodField()
    description_fourth_period = serializers.SerializerMethodField()
    description_integrate = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    day_reasons = serializers.SerializerMethodField()

    def get_description_first_period(self, obj):
        if obj.foodinclusiondescription_set.filter(period__value=PeriodoEscolar.FIRST_PERIOD).exists():
            return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.get(
                period__value=PeriodoEscolar.FIRST_PERIOD)).data
        return None

    def get_description_second_period(self, obj):
        if obj.foodinclusiondescription_set.filter(period__value=PeriodoEscolar.SECOND_PERIOD).exists():
            return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.get(
                period__value=PeriodoEscolar.SECOND_PERIOD)).data
        return None

    def get_description_third_period(self, obj):
        if obj.foodinclusiondescription_set.filter(period__value=PeriodoEscolar.THIRD_PERIOD).exists():
            return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.get(
                period__value=PeriodoEscolar.THIRD_PERIOD)).data
        return None

    def get_description_fourth_period(self, obj):
        if obj.foodinclusiondescription_set.filter(period__value=PeriodoEscolar.FOURTH_PERIOD).exists():
            return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.get(
                period__value=PeriodoEscolar.FOURTH_PERIOD)).data
        return None

    def get_description_integrate(self, obj):
        if obj.foodinclusiondescription_set.filter(period__value=PeriodoEscolar.INTEGRATE).exists():
            return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.get(
                period__value=PeriodoEscolar.INTEGRATE)).data
        return None

    def get_day_reasons(self, obj):
        if obj.foodinclusiondayreason_set.exists():
            return FoodInclusionDayReasonSerializer(obj.foodinclusiondayreason_set.all(), many=True).data
        return None

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y às %H:%M")

    def get_status(self, obj):
        return obj.status.name if obj.status else None

    class Meta:
        model = InclusaoAlimentacao
        fields = (
            'id', 'uuid', 'created_at', 'description_first_period', 'description_second_period',
            'description_third_period', 'description_fourth_period', 'description_integrate',
            'status', 'obs', 'day_reasons')
