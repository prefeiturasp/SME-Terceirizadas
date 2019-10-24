from notifications.models import Notification
from rest_framework import serializers

from .validators import senha_deve_ser_igual_confirmar_senha
from ..models import (Perfil, Usuario)


class PerfilSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nome', 'uuid')


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        exclude = ('id', 'ativo')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ('actor_object_id', 'target_object_id', 'action_object_object_id', 'recipient',
                   'actor_content_type', 'target_content_type', 'action_object_content_type')


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('uuid', 'nome', 'email', 'date_joined')


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    confirmar_password = serializers.CharField()

    def partial_update(self, validated_data, usuario):
        password = validated_data.get('password')
        confirmar_password = validated_data.pop('confirmar_password')
        senha_deve_ser_igual_confirmar_senha(password, confirmar_password)
        self.update(usuario, validated_data)
        usuario.set_password(validated_data['password'])
        usuario.save()
        return usuario

    class Meta:
        model = Usuario
        fields = ('email', 'registro_funcional', 'vinculo_funcional', 'password', 'confirmar_password', 'cpf')
        write_only_fields = ('password',)
