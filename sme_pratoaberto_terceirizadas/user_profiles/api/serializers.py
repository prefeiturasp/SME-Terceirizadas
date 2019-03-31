from rest_framework import serializers

from ..models import SchoolProfile


class SchoolProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolProfile
        fields = ['eol_code', 'codae_code', 'school_name', 'username']
