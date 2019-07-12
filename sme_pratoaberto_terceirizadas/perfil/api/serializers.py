from rest_framework import serializers

from ..models import Usuario, Perfil, Permissao, GrupoPerfil


class UsuarioSerializer(serializers.ModelSerializer):
    # TODO:     "groups": [],
    # "user_permissions": [],
    # "perfis": []
    # date_joined -> ptbr
    class Meta:
        model = Usuario
        fields = ('uuid', 'nome', 'email', 'date_joined')


class PermissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissao
        exclude = ('id', 'ativo')


class PerfilSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nome', 'uuid')


class GrupoCompletoPerfilSerializer(serializers.ModelSerializer):
    perfis = PerfilSimplesSerializer(many=True)

    class Meta:
        model = GrupoPerfil
        exclude = ('id', 'ativo')


class GrupoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoPerfil
        exclude = ('id', 'ativo')


class PerfilSerializer(serializers.ModelSerializer):
    permissoes = PermissaoSerializer(many=True)
    grupo = GrupoSimplesSerializer()

    class Meta:
        model = Perfil
        exclude = ('id', 'ativo')

#
# class NotificationSerializer(serializers.Serializer):
#     unread = serializers.BooleanField(read_only=True)
#     action_object = GenericNotificationRelatedField(read_only=True)
#     description = serializers.SerializerMethodField()
#
#     def get_description(self, obj):
#         return obj.description

#
# class PrivateUserSerializer(serializers.ModelSerializer):
#     notifications = NotificationSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = settings.AUTH_USER_MODEL
#         fields = ('name', 'email', 'profile', 'notifications')
