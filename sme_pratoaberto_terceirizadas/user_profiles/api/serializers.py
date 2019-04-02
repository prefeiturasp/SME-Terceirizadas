from rest_framework import serializers

from sme_pratoaberto_terceirizadas.school.models import School


class SchoolProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['eol_code', 'codae_code', 'school_name', 'username']
