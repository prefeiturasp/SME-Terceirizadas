from notifications.models import Notification
from rest_framework import serializers
from .models import User
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit
from sme_pratoaberto_terceirizadas.meal_kit.serializers import MealKitSerializer


class GenericNotificationRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, MealKit):
            serializer = MealKitSerializer(value)

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
        model = User
        fields = ('name', 'email', 'profile', 'notifications')
