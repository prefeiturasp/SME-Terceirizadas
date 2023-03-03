import re

from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ....dados_comuns.api.serializers import ContatoSerializer
from ....dados_comuns.constants import ADMINISTRADOR_EMPRESA
from ....dados_comuns.models import Contato
from ....dados_comuns.utils import update_instance_from_dict
from ....escola.models import DiretoriaRegional, Lote
from ....perfil.api.serializers import SuperAdminTerceirizadaSerializer, UsuarioUpdateSerializer
from ....perfil.models import Perfil, Usuario
from ...models import (
    Contrato,
    Edital,
    EmailTerceirizadaPorModulo,
    Modulo,
    Nutricionista,
    Terceirizada,
    VigenciaContrato
)


def cria_contatos(contatos):
    contatos_list = []
    for contato_json in contatos:
        contato = ContatoSerializer().create(contato_json)
        contatos_list.append(contato)
    return contatos_list


class NutricionistaCreateSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)

    def create(self, validated_data):
        contatos = validated_data.pop('contatos', [])
        nutricionista = Nutricionista.objects.create(**validated_data)
        for contato_json in contatos:
            contato = ContatoSerializer().create(
                validated_data=contato_json)
            nutricionista.contatos.add(contato)
        return nutricionista

    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class VigenciaContratoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VigenciaContrato
        exclude = ('id', 'contrato')


class ContratoCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Lote.objects.all()
    )

    terceirizada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Terceirizada.objects.all()
    )

    diretorias_regionais = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=DiretoriaRegional.objects.all()
    )

    vigencias = VigenciaContratoCreateSerializer(many=True)

    def create(self, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        dres_json = validated_data.pop('diretorias_regionais', [])
        vigencias_array = validated_data.pop('vigencias')

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        contrato = Contrato.objects.create(**validated_data)
        contrato.vigencias.set(vigencias)
        contrato.lotes.set(lotes_json)
        contrato.diretorias_regionais.set(dres_json)

        return contrato

    def update(self, instance, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        terceirizadas_json = validated_data.pop('terceirizadas', [])
        dres_json = validated_data.pop('diretorias_regionais', [])

        vigencias_array = validated_data.pop('vigencias')

        instance.vigencias.all().delete()

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        update_instance_from_dict(instance, validated_data, save=True)

        instance.contratos.set(vigencias)
        instance.lotes.set(lotes_json)
        instance.terceirizadas.set(terceirizadas_json)
        instance.diretorias_regionais.set(dres_json)

        return instance

    class Meta:
        model = Contrato
        exclude = ('id',)


class ContratoAbastecimentoCreateSerializer(serializers.ModelSerializer):
    vigencias = VigenciaContratoCreateSerializer(many=True)

    def create(self, validated_data):
        vigencias_array = validated_data.pop('vigencias')

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        contrato = Contrato.objects.create(**validated_data)
        contrato.vigencias.set(vigencias)

        return contrato

    class Meta:
        model = Contrato
        exclude = ('id',)


class TerceirizadaCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(slug_field='uuid', many=True, queryset=Lote.objects.all())
    contatos = ContatoSerializer(many=True)
    super_admin = SuperAdminTerceirizadaSerializer()

    def create(self, validated_data):
        super_admin = validated_data.pop('super_admin')
        lotes = validated_data.pop('lotes', [])
        contatos = validated_data.pop('contatos', [])

        terceirizada = Terceirizada.objects.create(**validated_data)

        checar_terceirizadas_inativacao = self.checar_terceirizadas_para_inativacao(terceirizada, lotes)

        terceirizada.lotes.set(lotes)

        """ Inativa terceirizadas que nao tem lote """
        Terceirizada.objects.filter(
            uuid__in=checar_terceirizadas_inativacao, lotes__isnull=True).update(ativo=False)

        contatos_list = cria_contatos(contatos)
        terceirizada.contatos.set(contatos_list)

        self.criar_super_admin_terceirizada(super_admin, terceirizada)

        return terceirizada

    def update(self, instance, validated_data):
        # TODO: Analisar complexidade
        # TODO: voltar aqui quando uma terceirizada tiver seu painel admin para criar suas nutris
        # aqui está tratando nutris como um dado escravo da Terceirizada
        super_admin_data = validated_data.pop('super_admin')
        lotes_array = validated_data.pop('lotes', [])
        contatos = validated_data.pop('contatos', [])

        instance.contatos.clear()

        if instance.lotes.exclude(id__in=[lote.id for lote in lotes_array]).exists():
            raise ValidationError('Não pode remover um lote de uma empresa. É preciso atribuí-lo a outra empresa.')

        checar_terceirizadas_inativacao = self.checar_terceirizadas_para_inativacao(instance, lotes_array)

        update_instance_from_dict(instance, validated_data, save=True)

        contatos_list = cria_contatos(contatos)
        instance.contatos.set(contatos_list)
        instance.lotes.set(lotes_array)

        """ Inativa terceirizadas que nao tem lote """
        Terceirizada.objects.filter(
            uuid__in=checar_terceirizadas_inativacao, lotes__isnull=True).update(ativo=False)

        if instance.super_admin:
            self.atualizar_super_admin_terceirizada(super_admin_data, instance)
        else:
            self.criar_super_admin_terceirizada(super_admin_data, instance)

        return instance

    def criar_super_admin_terceirizada(self, dados_usuario, terceirizada): # noqa C901
        contatos = dados_usuario.pop('contatos')
        dados_usuario['username'] = dados_usuario['cpf']
        try:
            usuario = Usuario.objects.create(**dados_usuario)
        except IntegrityError as e:
            if re.search('perfil_usuario_cpf_key.+already\\sexists', e.args[0], flags=re.I | re.S):
                raise serializers.ValidationError(f'CPF - {dados_usuario["cpf"]} - já cadastrado')
            if re.search('perfil_usuario_email_key.+already\\sexists', e.args[0], flags=re.I | re.S):
                raise serializers.ValidationError(f'Email - {dados_usuario["email"]} - já cadastrado')
            raise e
        usuario.super_admin_terceirizadas = True
        usuario.is_active = False
        usuario.save()
        for contato in contatos:
            contato = ContatoSerializer().create(contato)
            usuario.contatos.add(contato)
        usuario.criar_vinculo_administrador(
            terceirizada,
            nome_perfil=ADMINISTRADOR_EMPRESA
        )
        usuario.enviar_email_administrador()

    def atualizar_super_admin_terceirizada(self, dados_usuario, terceirizada): # noqa C901
        dados_usuario_original = dados_usuario.copy()
        contatos = dados_usuario.pop('contatos')
        email = dados_usuario.get('email')
        cpf = dados_usuario.get('cpf')
        nome = dados_usuario.get('nome')
        cargo = dados_usuario.get('cargo')

        super_admin = terceirizada.super_admin
        super_admin.contatos.clear()

        novo_email = False

        if cpf != super_admin.cpf:
            if Usuario.objects.filter(cpf=cpf).exists():
                raise ValidationError('Usuario com este CPF já existe.')
        if email != super_admin.email:
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError('Usuario com este Email já existe.')
            novo_email = True

        if novo_email:
            self.criar_super_admin_terceirizada(dados_usuario_original, terceirizada)
        else:
            super_admin.nome = nome
            super_admin.email = email
            super_admin.cpf = cpf
            super_admin.cargo = cargo
            super_admin.crn_numero = None
            vinculo_atual = super_admin.vinculo_atual
            vinculo_atual.perfil = Perfil.objects.get(nome='ADMINISTRADOR_EMPRESA')
            vinculo_atual.perfil.save()
            vinculo_atual.save()
            super_admin.save()
            for contato in contatos:
                email = contato.get('email', '')
                telefone = contato.get('telefone', '')
                contato = Contato.objects.create(email=email, telefone=telefone)
                super_admin.contatos.add(contato)

    def checar_terceirizadas_para_inativacao(self, terceirizada, lotes):
        checar_terceirizadas_inativacao = []
        for lote in [lote for lote in lotes if lote not in terceirizada.lotes.all() and lote.terceirizada]:
            checar_terceirizadas_inativacao.append(lote.terceirizada.uuid)
            lote.transferir_solicitacoes_gestao_alimentacao(terceirizada)
            lote.transferir_dietas_especiais(terceirizada)

        return checar_terceirizadas_inativacao

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class EmpresaNaoTerceirizadaCreateSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)
    contratos = ContratoAbastecimentoCreateSerializer(many=True, required=False)

    def create(self, validated_data):
        contatos = validated_data.pop('contatos', [])
        contratos_array = validated_data.pop('contratos', [])

        empresa = Terceirizada.objects.create(**validated_data)
        contatos_list = cria_contatos(contatos)
        empresa.contatos.set(contatos_list)

        self.cria_ou_atualiza_responsavel_empresa(empresa, validated_data, contatos, eh_update=False)
        contratos = []
        for contrato_json in contratos_array:
            contrato = ContratoAbastecimentoCreateSerializer().create(contrato_json)
            contratos.append(contrato)

        empresa.contratos.set(contratos)

        return empresa

    def update(self, instance, validated_data):
        contatos = validated_data.pop('contatos', [])
        contratos_array = validated_data.pop('contratos', [])

        contratos = []
        for contrato_json in contratos_array:
            encerrado = contrato_json.pop('encerrado')
            if not encerrado:
                contrato = ContratoAbastecimentoCreateSerializer().create(contrato_json)
                contratos.append(contrato)

        instance.contatos.all().delete()
        instance.contratos.filter(encerrado=False).delete()
        update_instance_from_dict(instance, validated_data, save=True)
        contatos_list = cria_contatos(contatos)
        instance.contatos.set(contatos_list)
        self.cria_ou_atualiza_responsavel_empresa(instance, validated_data, contatos_list, eh_update=True)
        for contrato in contratos:
            instance.contratos.add(contrato)

        return instance

    def cria_ou_atualiza_responsavel_empresa(self, empresa, validated_data, contatos, eh_update=False):
        responsavel_empresa_json = {
            'cpf': validated_data.get('responsavel_cpf', None),
            'nome': validated_data.get('responsavel_nome', None),
            'email': validated_data.get('responsavel_email', None),
            'contatos': contatos
        }
        if eh_update:
            UsuarioUpdateSerializer().update_distribuidor(empresa, responsavel_empresa_json)
        else:
            UsuarioUpdateSerializer().create_distribuidor(empresa, responsavel_empresa_json)

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class EditalContratosCreateSerializer(serializers.ModelSerializer):
    contratos = ContratoCreateSerializer(many=True)

    def create(self, validated_data):
        contratos_array = validated_data.pop('contratos')

        contratos = []
        for contrato_json in contratos_array:
            contrato = ContratoCreateSerializer().create(contrato_json)
            contratos.append(contrato)

        edital = Edital.objects.create(**validated_data)
        edital.contratos.set(contratos)
        return edital

    def update(self, instance, validated_data):
        contrato_array = validated_data.pop('contratos')

        instance.contratos.all().delete()

        contratos = []
        for contrato_json in contrato_array:
            contrato = ContratoCreateSerializer().create(contrato_json)
            contratos.append(contrato)

        update_instance_from_dict(instance, validated_data, save=True)

        instance.contratos.set(contratos)

        return instance

    class Meta:
        model = Edital
        exclude = ('id',)


class CreateEmailTerceirizadaPorModuloSerializer(serializers.ModelSerializer):
    terceirizada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Terceirizada.objects.all()
    )
    modulo = serializers.SlugRelatedField(
        slug_field='nome',
        required=True,
        queryset=Modulo.objects.all()
    )
    criado_por = serializers.CharField(required=False)

    def create(self, validated_data):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        validated_data['criado_por'] = user
        EmailTerceirizada = EmailTerceirizadaPorModulo.objects.create(**validated_data)
        return EmailTerceirizada

    class Meta:
        model = EmailTerceirizadaPorModulo
        exclude = ('id',)
