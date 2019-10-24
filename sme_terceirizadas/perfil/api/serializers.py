from notifications.models import Notification
from rest_framework import serializers

from .validators import (
    registro_funcional_e_cpf_sao_da_mesma_pessoa, senha_deve_ser_igual_confirmar_senha,
    usuario_pode_efetuar_cadastro
)
from ..models import (GrupoPerfil, Perfil, PerfilPermissao, Permissao, Usuario)


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


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('uuid', 'nome', 'email', 'date_joined')


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


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    confirmar_password = serializers.CharField()

    def validate(self, instance, attrs):
        senha_deve_ser_igual_confirmar_senha(attrs['password'], attrs['confirmar_password'])
        registro_funcional_e_cpf_sao_da_mesma_pessoa(instance, attrs['registro_funcional'], attrs['cpf'])
        usuario_pode_efetuar_cadastro(instance)
        attrs['email'] = attrs['email'] + '@sme.prefeitura.sp.gov.br'
        return attrs

    def partial_update(self, instance, validated_data):
        validated_data = self.validate(instance, validated_data)
        self.update(instance, validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = Usuario
        fields = ('email', 'registro_funcional', 'password', 'confirmar_password', 'cpf')
        write_only_fields = ('password',)
