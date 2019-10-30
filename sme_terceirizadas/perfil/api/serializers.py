from notifications.models import Notification
from rest_framework import serializers

from sme_terceirizadas.escola.api.validators import deve_ser_mesma_instituicao
from ...eol_servico.utils import get_informacoes_usuario
from .validators import (
    deve_ser_email_sme, registro_funcional_e_cpf_sao_da_mesma_pessoa, senha_deve_ser_igual_confirmar_senha,
    usuario_pode_efetuar_cadastro
)
from ..models import Perfil, Usuario, Vinculo


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


class VinculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vinculo
        fields = ('data_inicial', 'data_final', 'usuario')


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    confirmar_password = serializers.CharField()

    def create(self, validated_data):
        informacoes_usuario = get_informacoes_usuario(validated_data['registro_funcional'])
        informacoes_usuario = informacoes_usuario.json()['results'][0]
        nome_escola = validated_data.pop('escola')
        deve_ser_mesma_instituicao(
            instituicao_objeto=nome_escola,
            instituicao_eol=informacoes_usuario['divisao']
        )
        cpf = informacoes_usuario['cd_cpf_pessoa']
        if Usuario.objects.filter(cpf=cpf).exists():
            usuario = Usuario.objects.get(cpf=cpf)
        else:
            email = f'{cpf}@dev.prefeitura.sp.gov.br'
            usuario = Usuario.objects.create_user(email, 'adminadmin')
        usuario.registro_funcional = validated_data['registro_funcional']
        usuario.nome = informacoes_usuario['nm_pessoa']
        usuario.cpf = cpf
        usuario.is_active = False
        usuario.save()
        return usuario

    def _validate(self, instance, attrs):
        senha_deve_ser_igual_confirmar_senha(attrs['password'], attrs['confirmar_password'])
        registro_funcional_e_cpf_sao_da_mesma_pessoa(instance, attrs['registro_funcional'], attrs['cpf'])
        usuario_pode_efetuar_cadastro(instance)
        deve_ser_email_sme(attrs['email'])
        return attrs

    def partial_update(self, instance, validated_data):
        validated_data = self._validate(instance, validated_data)
        self.update(instance, validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = Usuario
        fields = ('email', 'registro_funcional', 'password', 'confirmar_password', 'cpf')
        write_only_fields = ('password',)
