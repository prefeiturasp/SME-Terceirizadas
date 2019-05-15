from rest_framework import serializers

from sme_pratoaberto_terceirizadas.school.models import School, SchoolPeriod


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = '__all__'


class SchoolPeriodSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.name

    class Meta:
        model = SchoolPeriod
        fields = ('label', 'value')
