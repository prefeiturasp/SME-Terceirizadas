from notifications.models import Notification
from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.api.serializers import (
    EscolaSimplesSerializer, DiretoriaRegionalSimplesSerializer)
from ..models import (Usuario, Perfil, Permissao, GrupoPerfil, PerfilPermissao)


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
        exclude = ('actor_object_id', 'target_object_id', 'action_object_object_id', 'recipient',
                   'actor_content_type', 'target_content_type', 'action_object_content_type')


class UsuarioDetalheSerializer(serializers.ModelSerializer):
    perfis = PerfilSerializer(many=True, read_only=True)
    escolas = EscolaSimplesSerializer(many=True)
    diretorias_regionais = DiretoriaRegionalSimplesSerializer(many=True)

    class Meta:
        model = Usuario
        fields = ('uuid', 'nome', 'email', 'date_joined', 'perfis', 'escolas', 'diretorias_regionais')
