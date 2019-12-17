from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .validators import (
    registro_funcional_e_cpf_sao_da_mesma_pessoa,
    senha_deve_ser_igual_confirmar_senha,
    terceirizada_tem_esse_cnpj,
    usuario_pode_efetuar_cadastro
)
from ..models import Perfil, Usuario, Vinculo
from ...dados_comuns.constants import ADMINISTRADOR_TERCEIRIZADA, NUTRI_ADMIN_RESPONSAVEL
from ...dados_comuns.models import Contato
from ...eol_servico.utils import EolException, get_informacoes_usuario
from ...escola.api.validators import usuario_e_vinculado_a_aquela_instituicao, usuario_nao_possui_vinculo_valido
from ...terceirizada.models import Terceirizada


class PerfilSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nome', 'uuid')


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        exclude = ('id', 'nome', 'ativo')


class UsuarioSerializer(serializers.ModelSerializer):
    cpf = serializers.SerializerMethodField()

    def get_cpf(self, obj):
        if obj.vinculo_atual and isinstance(obj.vinculo_atual.instituicao, Terceirizada):
            return obj.cpf
        return None

    class Meta:
        model = Usuario
        fields = ('uuid', 'cpf', 'nome', 'email', 'date_joined', 'registro_funcional', 'tipo_usuario')


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

    def atualizar_nutricionista(self, usuario, validated_data):
        if validated_data.get('contatos', None):
            usuario.email = validated_data['contatos'][0]['email']
        else:
            usuario.email = validated_data.get('email')
        usuario.cpf = validated_data.get('cpf', None)
        usuario.registro_funcional = None
        usuario.nome = validated_data['nome']
        usuario.crn_numero = validated_data.get('crn_numero', None)
        usuario.super_admin_terceirizadas = validated_data.get('super_admin_terceirizadas', False)
        usuario.save()
        for contato_json in validated_data.get('contatos', []):
            contato = Contato(
                email=contato_json['email'],
                telefone=contato_json['telefone']
            )
            contato.save()
            usuario.contatos.add(contato)
        return usuario

    def create_nutricionista(self, terceirizada, validated_data):
        if validated_data.get('contatos', None):
            email = validated_data['contatos'][0]['email']
        else:
            email = validated_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('E-mail já cadastrado')
        usuario = Usuario()
        usuario = self.atualizar_nutricionista(usuario, validated_data)
        usuario.is_active = False
        usuario.save()
        if usuario.super_admin_terceirizadas:
            usuario.criar_vinculo_administrador(terceirizada, nome_perfil=NUTRI_ADMIN_RESPONSAVEL)
        else:
            usuario.criar_vinculo_administrador(terceirizada, nome_perfil=ADMINISTRADOR_TERCEIRIZADA)
        usuario.enviar_email_administrador()

    def update_nutricionista(self, terceirizada, validated_data):
        novo_usuario = False
        email = validated_data['contatos'][0]['email']
        if Usuario.objects.filter(email=email).exists():
            usuario = Usuario.objects.get(email=email)
            usuario.contatos.all().delete()
        else:
            usuario = Usuario()
            usuario.is_active = False
            novo_usuario = True
        usuario = self.atualizar_nutricionista(usuario, validated_data)
        nome_perfil = NUTRI_ADMIN_RESPONSAVEL if validated_data.get(
            'super_admin_terceirizadas') else ADMINISTRADOR_TERCEIRIZADA
        if novo_usuario:
            usuario.criar_vinculo_administrador(terceirizada, nome_perfil=nome_perfil)
            usuario.enviar_email_administrador()
        else:
            vinculo = usuario.vinculo_atual
            vinculo.perfil = Perfil.objects.get(nome=nome_perfil)
            vinculo.save()

    def create(self, validated_data):  # noqa C901
        # TODO: ajeitar isso aqui, criar um validator antes...
        try:
            informacoes_usuario = self.get_informacoes_usuario(validated_data)
        except EolException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
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
        cnpj = attrs.get('cnpj', None)
        if cnpj:
            terceirizada_tem_esse_cnpj(instance.vinculo_atual.instituicao, cnpj)
        if 'tipo_email' in attrs:
            registro_funcional_e_cpf_sao_da_mesma_pessoa(instance, attrs['registro_funcional'], attrs['cpf'])
            usuario_pode_efetuar_cadastro(instance)
        return attrs

    def partial_update(self, instance, validated_data):
        cnpj = validated_data.get('cnpj', None)
        validated_data = self._validate(instance, validated_data)
        self.update(instance, validated_data)
        instance.set_password(validated_data['password'])
        if cnpj:
            instance.vinculo_atual.ativar_vinculo()
            instance.is_active = True
        instance.save()
        return instance

    class Meta:
        model = Usuario
        fields = ('email', 'registro_funcional', 'password', 'confirmar_password', 'cpf')
        write_only_fields = ('password',)
