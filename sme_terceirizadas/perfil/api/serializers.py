import logging
import re

from django.db import transaction
from django.db.utils import IntegrityError
from munch import Munch
from requests import ConnectTimeout, ReadTimeout
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from sme_terceirizadas.perfil.models.usuario import (
    ImportacaoPlanilhaUsuarioExternoCoreSSO,
    ImportacaoPlanilhaUsuarioServidorCoreSSO
)

from ...dados_comuns.constants import (
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_DISTRIBUIDORA,
    ADMINISTRADOR_DRE,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    ADMINISTRADOR_GESTAO_PRODUTO,
    ADMINISTRADOR_SUPERVISAO_NUTRICAO,
    ADMINISTRADOR_TERCEIRIZADA
)
from ...dados_comuns.models import Contato
from ...eol_servico.utils import EOLException, EOLService, EOLServicoSGP
from ...perfil.api.validators import usuario_com_coresso_validation, usuario_e_das_terceirizadas
from ...terceirizada.models import Terceirizada
from ..models import Perfil, Usuario, Vinculo
from ..services.usuario_coresso_service import EOLUsuarioCoreSSO
from .validators import (
    deve_ser_email_sme_ou_prefeitura,
    deve_ter_mesmo_cpf,
    registro_funcional_e_cpf_sao_da_mesma_pessoa,
    senha_deve_ser_igual_confirmar_senha,
    terceirizada_tem_esse_cnpj,
    usuario_e_vinculado_a_aquela_instituicao,
    usuario_nao_possui_vinculo_valido,
    usuario_pode_efetuar_cadastro
)

logger = logging.getLogger(__name__)


class PerfilSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nome', 'visao', 'uuid')


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
        fields = (
            'uuid',
            'cpf',
            'nome',
            'email',
            'date_joined',
            'registro_funcional',
            'tipo_usuario',
            'cargo',
            'crn_numero'
        )


class UsuarioVinculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            'uuid',
            'cpf',
            'nome',
            'email',
            'date_joined',
            'registro_funcional',
            'tipo_usuario',
            'cargo'
        )


class VinculoSerializer(serializers.ModelSerializer):
    perfil = PerfilSimplesSerializer()
    usuario = UsuarioVinculoSerializer()

    class Meta:
        model = Vinculo
        fields = ('uuid', 'data_inicial', 'data_final', 'perfil', 'usuario')


class VinculoSimplesSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username')
    nome_usuario = serializers.CharField(source='usuario.nome')
    email_usuario = serializers.CharField(source='usuario.email')
    cpf_usuario = serializers.CharField(source='usuario.cpf')
    uuid_usuario = serializers.CharField(source='usuario.uuid')
    cnpj_empresa = serializers.SerializerMethodField()
    nome_perfil = serializers.CharField(source='perfil.nome')
    visao_perfil = serializers.CharField(source='perfil.visao')

    def get_cnpj_empresa(self, obj):
        if obj.content_type.name == 'Terceirizada':
            return obj.instituicao.cnpj
        return None

    class Meta:
        model = Vinculo
        fields = ('uuid', 'username', 'nome_usuario', 'email_usuario', 'cpf_usuario', 'uuid_usuario', 'cnpj_empresa',
                  'nome_perfil', 'visao_perfil', )


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    confirmar_password = serializers.CharField()

    def get_informacoes_usuario(self, validated_data):
        return EOLService.get_informacoes_usuario(validated_data['registro_funcional'])

    def atualizar_nutricionista(self, usuario, validated_data):
        if validated_data.get('contatos', None):
            usuario.email = validated_data['contatos'][0]['email']
        else:
            usuario.email = validated_data.get('email')
        usuario.cpf = validated_data.get('cpf', None)
        usuario.registro_funcional = None
        usuario.nome = validated_data['nome']
        usuario.crn_numero = validated_data.get('crn_numero', None)
        usuario.save()
        for contato_json in validated_data.get('contatos', []):
            contato = Contato(
                email=contato_json['email'],
                telefone=contato_json['telefone']
            )
            contato.save()
            usuario.contatos.add(contato)
        return usuario

    def atualizar_distribuidor(self, usuario, validated_data):
        usuario.email = validated_data.get('email')
        usuario.cpf = validated_data.get('cpf', None)
        usuario.registro_funcional = None
        usuario.nome = validated_data['nome']
        usuario.crn_numero = validated_data.get('crn_numero', None)
        usuario.super_admin_terceirizadas = True
        usuario.save()
        contatos = validated_data.get('contatos', [])

        usuario.contatos.set(contatos)
        return usuario

    def criar_distribuidor(self, usuario, validated_data):
        usuario.email = validated_data.get('email')
        usuario.cpf = validated_data.get('cpf', None)
        usuario.registro_funcional = None
        usuario.nome = validated_data['nome']
        usuario.crn_numero = validated_data.get('crn_numero', None)
        usuario.super_admin_terceirizadas = True
        usuario.save()
        contatos = validated_data.get('contatos', None)
        contatos_obj = []
        for contato in contatos:
            email = contato.get('email', None)
            telefone = contato.get('telefone', None)
            contato = Contato(
                email=email,
                telefone=telefone
            )
            contato.save()
            contatos_obj.append(contato)
        usuario.contatos.set(contatos_obj)
        return usuario

    def create_nutricionista(self, terceirizada, validated_data):
        if validated_data.get('contatos', None):
            email = validated_data['contatos'][0]['email']
        else:
            email = validated_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Já existe um nutricionista com este email: ' + email)
        usuario = Usuario()
        usuario = self.atualizar_nutricionista(usuario, validated_data)
        usuario.is_active = False
        usuario.save()
        usuario.criar_vinculo_administrador(
            terceirizada,
            nome_perfil=ADMINISTRADOR_TERCEIRIZADA
        )

    def create_distribuidor(self, terceirizada, validated_data):
        email = validated_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('E-mail já cadastrado')
        usuario = Usuario()
        usuario = self.criar_distribuidor(usuario, validated_data)
        usuario.is_active = False
        usuario.save()
        if usuario.super_admin_terceirizadas:
            usuario.criar_vinculo_administrador(
                terceirizada,
                nome_perfil=ADMINISTRADOR_DISTRIBUIDORA
            )
        else:
            usuario.criar_vinculo_administrador(
                terceirizada,
                nome_perfil=ADMINISTRADOR_TERCEIRIZADA
            )
        usuario.enviar_email_administrador()

    def update_distribuidor(self, terceirizada, validated_data):
        nome_perfil = ADMINISTRADOR_DISTRIBUIDORA
        novo_usuario = False
        email = validated_data.get('email')
        cpf = validated_data.get('cpf', None)
        if Usuario.objects.filter(email=email).exists():
            usuario = Usuario.objects.get(email=email)
            usuario.contatos.all().delete()
        elif Usuario.objects.filter(cpf=cpf).exists():
            usuario = Usuario.objects.get(cpf=cpf)
            usuario.contatos.all().delete()
            vinculo = Vinculo.objects.filter(object_id=terceirizada.id).last()
            vinculo.finalizar_vinculo()
            novo_usuario = True
        else:
            usuario = Usuario()
            usuario.is_active = False
            vinculo = Vinculo.objects.filter(object_id=terceirizada.id).last()
            vinculo.finalizar_vinculo()
            novo_usuario = True
        usuario = self.atualizar_distribuidor(usuario, validated_data)
        if novo_usuario:
            usuario.criar_vinculo_administrador(
                terceirizada,
                nome_perfil=nome_perfil
            )
            usuario.enviar_email_administrador()

    def update_nutricionista(self, terceirizada, validated_data):
        novo_usuario = False
        email = validated_data['contatos'][0]['email']
        if Usuario.objects.filter(email=email, super_admin_terceirizadas=False).exists():
            usuario = Usuario.objects.get(email=email, super_admin_terceirizadas=False)
            usuario.contatos.all().delete()
        else:
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError('Já existe um usuario com este email: ' + email)
            usuario = Usuario()
            usuario.is_active = False
            novo_usuario = True
        usuario = self.atualizar_nutricionista(usuario, validated_data)
        if novo_usuario:
            usuario.criar_vinculo_administrador(
                terceirizada,
                nome_perfil=ADMINISTRADOR_TERCEIRIZADA
            )
        else:
            vinculo = usuario.vinculo_atual
            vinculo.perfil = Perfil.objects.get(nome=ADMINISTRADOR_TERCEIRIZADA)
            vinculo.save()

    def create(self, validated_data):  # noqa C901
        # TODO: ajeitar isso aqui, criar um validator antes...
        try:
            informacoes_usuario_json = self.get_informacoes_usuario(validated_data)  # noqa
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        eh_da_codae = validated_data['instituicao'] == 'CODAE'
        eh_da_dre = validated_data['instituicao'].startswith('DIRETORIA REGIONAL DE EDUCACAO')
        if not eh_da_codae and not eh_da_dre:
            usuario_e_vinculado_a_aquela_instituicao(
                descricao_instituicao=validated_data['instituicao'],
                instituicoes_eol=informacoes_usuario_json
            )
        cpf = informacoes_usuario_json[0]['cd_cpf_pessoa']
        if Usuario.objects.filter(cpf=cpf).exists():
            usuario = Usuario.objects.get(cpf=cpf)
            usuario_nao_possui_vinculo_valido(usuario)
            usuario.enviar_email_confirmacao()
        else:
            email = f'{cpf}@emailtemporario.prefeitura.sp.gov.br'
            usuario = Usuario.objects.create_user(email, 'adminadmin')
            usuario.registro_funcional = validated_data['registro_funcional']
            usuario.nome = informacoes_usuario_json[0]['nm_pessoa']
            usuario.cpf = cpf
            usuario.is_active = False
            usuario.save()
        return usuario

    def _validate(self, instance, attrs):  # noqa C901
        senha_deve_ser_igual_confirmar_senha(attrs['password'], attrs['confirmar_password'])  # noqa
        cpf = attrs.get('cpf')
        cnpj = attrs.get('cnpj', None)
        if cnpj:
            usuario_e_das_terceirizadas(instance)
            terceirizada_tem_esse_cnpj(instance.vinculo_atual.instituicao, cnpj)  # noqa
        if instance.cpf:
            deve_ter_mesmo_cpf(cpf, instance.cpf)
        if 'registro_funcional' in attrs:
            registro_funcional_e_cpf_sao_da_mesma_pessoa(instance, attrs['registro_funcional'], attrs['cpf'])  # noqa
            usuario_pode_efetuar_cadastro(instance)
        if instance.vinculo_atual.perfil.nome in [
            ADMINISTRADOR_DRE,
            ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
            ADMINISTRADOR_DIETA_ESPECIAL,
            ADMINISTRADOR_GESTAO_PRODUTO,
            ADMINISTRADOR_SUPERVISAO_NUTRICAO
        ]:
            deve_ser_email_sme_ou_prefeitura(attrs['email'])

        return attrs

    def partial_update(self, instance, validated_data):  # noqa C901
        cnpj = validated_data.get('cnpj', None)
        validated_data = self._validate(instance, validated_data)
        try:
            self.update(instance, validated_data)
        except IntegrityError as e:
            if re.search('perfil_usuario_cpf_key.+already\\sexists', e.args[0], flags=re.I | re.S):
                raise serializers.ValidationError('CPF já cadastrado')
            if re.search('perfil_usuario_email_key.+already\\sexists', e.args[0], flags=re.I | re.S):
                raise serializers.ValidationError('Email já cadastrado')
            raise e
        instance.set_password(validated_data['password'])
        if cnpj:
            instance.vinculo_atual.ativar_vinculo()
            instance.is_active = True
        instance.save()
        return instance

    class Meta:
        model = Usuario
        fields = (
            'email',
            'registro_funcional',
            'password',
            'confirmar_password',
            'cpf'
        )
        write_only_fields = ('password',)


class UsuarioContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        exclude = ('id',)


class SuperAdminTerceirizadaSerializer(serializers.ModelSerializer):
    contatos = UsuarioContatoSerializer(many=True)
    cpf = serializers.CharField(max_length=11, allow_blank=False)
    email = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)

    def validate_cpf(self, value):
        if self.context['request']._request.method == 'POST':
            if self.Meta.model.objects.filter(cpf=value).exists():
                raise ValidationError('Usuário com este CPF já existe.')
        return value

    def validate_email(self, value):
        if self.context['request']._request.method == 'POST':
            if self.Meta.model.objects.filter(email=value).exists():
                raise ValidationError('Usuário com este Email já existe.')
        return value

    class Meta:
        model = Usuario
        fields = (
            'uuid',
            'cpf',
            'nome',
            'email',
            'contatos',
            'cargo'
        )


class UsuarioComCoreSSOCreateSerializer(serializers.ModelSerializer):
    eh_servidor = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    username = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    nome = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    visao = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    subdivisao = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    perfil = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    instituicao = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    cpf = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
    email = serializers.EmailField(write_only=True, required=True, allow_blank=False, allow_null=False)
    cargo = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=False)

    def validate(self, attrs):
        visao = attrs.get('visao')
        subdivisao = attrs.get('subdivisao')
        usuario_com_coresso_validation(visao, subdivisao)

        return attrs

    class Meta:
        model = Usuario
        fields = ['uuid', 'username', 'email', 'nome', 'visao', 'subdivisao', 'perfil', 'instituicao', 'cpf', 'cargo',
                  'eh_servidor']

    @transaction.atomic # noqa
    def create(self, validated_data):
        dados_usuario_dict = {
            'login': validated_data['username'],
            'nome': validated_data['nome'],
            'email': validated_data['email'],
            'cargo': validated_data.get('cargo', None),
            'cpf': validated_data['cpf'],
            'perfil': validated_data['perfil'],
            'visao': validated_data['visao'],
            'subdivisao': validated_data.get('subdivisao', None),
            'instituicao': validated_data['instituicao'],
            'eh_servidor': validated_data['eh_servidor']
        }

        dados_usuario = Munch.fromDict(dados_usuario_dict)
        eh_servidor = validated_data['eh_servidor'] == 'S'

        try:
            usuario = Usuario.cria_ou_atualiza_usuario_sigpae(dados_usuario=dados_usuario_dict, eh_servidor=eh_servidor)
            Vinculo.cria_vinculo(usuario=usuario, dados_usuario=dados_usuario_dict)
            eolusuariocoresso = EOLUsuarioCoreSSO()
            eolusuariocoresso.cria_ou_atualiza_usuario_core_sso(
                dados_usuario=dados_usuario,
                login=dados_usuario.login,
                eh_servidor=dados_usuario.eh_servidor
            )
            logger.info(f'Usuário {validated_data["username"]} criado/atualizado no CoreSSO com sucesso.')

            return usuario

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error = str(e)
                msg = error.split('Key')
                raise IntegrityError('Erro, informação duplicada:' + msg[1])
            raise IntegrityError('Erro ao tentar criar/atualizar usuário: ' + str(e))

        except Exception as e:
            msg = f'Erro ao tentar criar/atualizar usuário {validated_data["username"]} no CoreSSO/SIGPAE: {str(e)}'
            logger.error(msg)
            raise serializers.ValidationError(msg)


class AlteraEmailSerializer(serializers.ModelSerializer):

    @transaction.atomic # noqa
    def update(self, instance, validated_data):
        try:
            instance.email = validated_data.get('email')
            instance.save()
            EOLServicoSGP.redefine_email(instance.username, validated_data['email'])
        except EOLException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'detail': 'Já existe um usuário com este e-mail'}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        return instance

    class Meta:
        model = Usuario
        fields = ['uuid', 'username', 'email']


class ImportacaoPlanilhaUsuarioServidorCoreSSOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportacaoPlanilhaUsuarioServidorCoreSSO
        exclude = ['id']


class ImportacaoPlanilhaUsuarioExternoCoreSSOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportacaoPlanilhaUsuarioExternoCoreSSO
        exclude = ['id']


class ImportacaoPlanilhaUsuarioServidorCoreSSOCreateSerializer(serializers.ModelSerializer):
    conteudo = serializers.FileField(required=True)

    def validate(self, attrs):
        conteudo = attrs.get('conteudo')
        if conteudo:
            if not conteudo.name.split('.')[-1] in ['.xlsx', '.xls']:
                raise serializers.ValidationError({'detail': 'Extensão do arquivo não suportada.'})

        return attrs

    class Meta:
        model = ImportacaoPlanilhaUsuarioServidorCoreSSO
        exclude = ('id',)


class ImportacaoPlanilhaUsuarioExternoCoreSSOCreateSerializer(serializers.ModelSerializer):
    conteudo = serializers.FileField(required=True)

    def validate(self, attrs):
        conteudo = attrs.get('conteudo')
        if conteudo:
            if not conteudo.name.split('.')[-1] in ['.xlsx', '.xls']:
                raise serializers.ValidationError({'detail': 'Extensão do arquivo não suportada.'})

        return attrs

    class Meta:
        model = ImportacaoPlanilhaUsuarioExternoCoreSSO
        exclude = ('id',)
