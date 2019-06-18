from rest_framework import serializers
from ..models import Permission


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['title', 'uuid']
