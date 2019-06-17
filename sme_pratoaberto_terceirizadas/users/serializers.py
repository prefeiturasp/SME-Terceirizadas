from django.conf import settings
from rest_framework import serializers

from sme_pratoaberto_terceirizadas.kit_lanche.models import KitLanche
from sme_pratoaberto_terceirizadas.kit_lanche.api.serializers import KitLancheSerializer
from .models import User


class GenericNotificationRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, KitLanche):
            serializer = KitLancheSerializer(value)

        return serializer.data


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'profile')


class NotificationSerializer(serializers.Serializer):
    unread = serializers.BooleanField(read_only=True)
    action_object = GenericNotificationRelatedField(read_only=True)
    description = serializers.SerializerMethodField()

    def get_description(self, obj):
        return obj.description


class PrivateUserSerializer(serializers.ModelSerializer):
    notifications = NotificationSerializer(many=True, read_only=True)

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ('name', 'email', 'profile', 'notifications')
