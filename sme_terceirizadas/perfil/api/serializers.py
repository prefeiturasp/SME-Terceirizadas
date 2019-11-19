from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .validators import (
    registro_funcional_e_cpf_sao_da_mesma_pessoa,
    senha_deve_ser_igual_confirmar_senha,
    usuario_pode_efetuar_cadastro
)
from ..models import Perfil, Usuario, Vinculo
from ...eol_servico.utils import get_informacoes_usuario
from ...escola.api.validators import usuario_e_vinculado_a_aquela_instituicao, usuario_nao_possui_vinculo_valido


class PerfilSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nome', 'uuid')


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        exclude = ('id', 'nome', 'ativo')


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('uuid', 'nome', 'email', 'date_joined', 'registro_funcional')


class VinculoSerializer(serializers.ModelSerializer):
    perfil = PerfilSimplesSerializer()
    usuario = UsuarioSerializer()

    class Meta:
        model = Vinculo
        fields = ('uuid', 'data_inicial', 'data_final', 'perfil', 'usuario')


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    confirmar_password = serializers.CharField()

    def get_informacoes_usuario(self, validated_data):
        return get_informacoes_usuario(validated_data['registro_funcional'])

    def create(self, validated_data):
        # TODO: ajeitar isso aqui, criar um validator antes...
        try:
            informacoes_usuario = self.get_informacoes_usuario(validated_data)
        except ValidationError as e:
            return Response({'detail': e.detail[0].title()}, status=status.HTTP_400_BAD_REQUEST)
        informacoes_usuario = informacoes_usuario.json()['results']
        if validated_data['instituicao'] != 'CODAE':
            usuario_e_vinculado_a_aquela_instituicao(
                descricao_instituicao=validated_data['instituicao'],
                instituicoes_eol=informacoes_usuario
            )
        cpf = informacoes_usuario[0]['cd_cpf_pessoa']
        if Usuario.objects.filter(cpf=cpf).exists():
            usuario = Usuario.objects.get(cpf=cpf)
            usuario_nao_possui_vinculo_valido(usuario)
            usuario.enviar_email_confirmacao()
        else:
            email = f'{cpf}@emailtemporario.prefeitura.sp.gov.br'
            usuario = Usuario.objects.create_user(email, 'adminadmin')
            usuario.registro_funcional = validated_data['registro_funcional']
            usuario.nome = informacoes_usuario[0]['nm_pessoa']
            usuario.cpf = cpf
            usuario.is_active = False
            usuario.save()
        return usuario

    def _validate(self, instance, attrs):
        senha_deve_ser_igual_confirmar_senha(attrs['password'], attrs['confirmar_password'])
        registro_funcional_e_cpf_sao_da_mesma_pessoa(instance, attrs['registro_funcional'], attrs['cpf'])
        usuario_pode_efetuar_cadastro(instance)
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
