from notifications.models import Notification
from rest_framework import serializers

from sme_pratoaberto_terceirizadas.perfil.models.perfil import PerfilPermissao
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


class GrupoPerfilCreateSerializer(serializers.ModelSerializer):
    perfis = serializers.SlugRelatedField(
        many=True, slug_field='uuid', queryset=Perfil.objects.all()
    )

    class Meta:
        model = GrupoPerfil
        exclude = ('id',)


class GrupoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoPerfil
        exclude = ('id', 'ativo')


class PerfilSerializer(serializers.ModelSerializer):
    grupo = GrupoSimplesSerializer()

    class Meta:
        model = Perfil
        exclude = ('id', 'ativo')


class PerfilPermissaoCreateSerializer(serializers.ModelSerializer):
    permissao = serializers.SlugRelatedField(slug_field='uuid', queryset=Permissao.objects.all())
    perfil = serializers.SlugRelatedField(slug_field='uuid', queryset=Perfil.objects.all())

    acoes_explicacao = serializers.CharField(
        source='acoes_choices_array_display',
        required=False,
        read_only=True)

    class Meta:
        model = PerfilPermissao
        exclude = ('id',)


class PerfilPermissaoSerializer(serializers.ModelSerializer):
    permissao = PermissaoSerializer()
    perfil = PerfilSerializer()
    acoes_explicacao = serializers.CharField(
        source='acoes_choices_array_display',
        required=False,
        read_only=True)

    class Meta:
        model = PerfilPermissao
        exclude = ('id',)


class GrupoCompletoPerfilSerializer(serializers.ModelSerializer):
    perfis = PerfilSerializer(many=True)

    class Meta:
        model = GrupoPerfil
        exclude = ('id',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
