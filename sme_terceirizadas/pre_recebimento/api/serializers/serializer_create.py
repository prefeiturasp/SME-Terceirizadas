from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSerializer
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EtapasDoCronograma,
    Laboratorio,
    LayoutDeEmbalagem,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    TipoDeEmbalagemDeLayout,
    TipoEmbalagemQld,
    UnidadeMedida
)
from sme_terceirizadas.produto.models import NomeDeProdutoEdital
from sme_terceirizadas.terceirizada.models import Contrato, Terceirizada

from ..helpers import cria_etapas_de_cronograma, cria_programacao_de_cronograma, cria_tipos_de_embalagens
from ..validators import contrato_pertence_a_empresa


class ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(serializers.ModelSerializer):
    data_programada = serializers.CharField(required=False)
    tipo_carga = serializers.ChoiceField(
        choices=ProgramacaoDoRecebimentoDoCronograma.TIPO_CARGA_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        exclude = ('id', 'cronograma')


class EtapasDoCronogramaCreateSerializer(serializers.ModelSerializer):
    numero_empenho = serializers.CharField(required=False)
    etapa = serializers.CharField(required=False)
    parte = serializers.CharField(required=False)
    data_programada = serializers.CharField(required=False)
    quantidade = serializers.FloatField(required=False)
    total_embalagens = serializers.IntegerField(required=False)

    class Meta:
        model = EtapasDoCronograma
        exclude = ('id', 'cronograma')


class CronogramaCreateSerializer(serializers.ModelSerializer):
    armazem = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Terceirizada.objects.filter(tipo_servico=Terceirizada.DISTRIBUIDOR_ARMAZEM),
        allow_null=True
    )
    empresa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Terceirizada.objects.filter(tipo_servico=Terceirizada.FORNECEDOR),
    )
    contrato = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Contrato.objects.all(),
        allow_null=True
    )
    produto = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=NomeDeProdutoEdital.objects.all(),
        allow_null=True
    )
    unidade_medida = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=UnidadeMedida.objects.all(),
        allow_null=True
    )
    password = serializers.CharField(required=False)
    qtd_total_programada = serializers.FloatField(required=False)
    tipo_embalagem = serializers.ChoiceField(
        choices=Cronograma.TIPO_EMBALAGEM_CHOICES, required=False, allow_blank=True)
    etapas = EtapasDoCronogramaCreateSerializer(many=True, required=False)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(many=True, required=False)
    cadastro_finalizado = serializers.BooleanField(required=False)

    def gera_proximo_numero_cronograma(self):
        ano = date.today().year
        ultimo_cronograma = Cronograma.objects.last()
        if ultimo_cronograma:
            return f'{str(int(ultimo_cronograma.numero[:3]) + 1).zfill(3)}/{ano}'
        else:
            return f'001/{ano}'

    def validate(self, attrs):
        user = self.context['request'].user
        cadastro_finalizado = attrs.get('cadastro_finalizado', None)
        if cadastro_finalizado and not user.verificar_autenticidade(attrs.pop('password', None)):
            raise NotAuthenticated(
                'Assinatura do cronograma não foi validada. Verifique sua senha.')
        return super().validate(attrs)

    def create(self, validated_data):
        contrato = validated_data.get('contrato', None)
        empresa = validated_data.get('empresa', None)
        contrato_pertence_a_empresa(contrato, empresa)
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])
        numero_cronograma = self.gera_proximo_numero_cronograma()
        cronograma = Cronograma.objects.create(numero=numero_cronograma, **validated_data)
        cronograma.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_CRIADO, usuario=user)

        cria_etapas_de_cronograma(etapas, cronograma)
        cria_programacao_de_cronograma(programacoes_de_recebimento, cronograma)

        if cadastro_finalizado:
            cronograma.inicia_fluxo(user=user)

        return cronograma

    def update(self, instance, validated_data):
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])

        instance.etapas.all().delete()
        instance.programacoes_de_recebimento.all().delete()

        update_instance_from_dict(instance, validated_data, save=True)

        cria_etapas_de_cronograma(etapas, instance)
        cria_programacao_de_cronograma(programacoes_de_recebimento, instance)

        if cadastro_finalizado:
            instance.inicia_fluxo(user=user)
        return instance

    class Meta:
        model = Cronograma
        exclude = ('id', 'numero', 'status')


class LaboratorioCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=True)
    cnpj = serializers.CharField(required=True)
    cep = serializers.CharField(required=True)
    logradouro = serializers.CharField(required=True)
    numero = serializers.CharField(required=True)
    bairro = serializers.CharField(required=True)
    cidade = serializers.CharField(required=True)
    estado = serializers.CharField(required=True)
    credenciado = serializers.BooleanField(required=True)
    contatos = ContatoSerializer(many=True)

    def cria_contatos(self, contatos, laboratorio):
        for contato_json in contatos:
            contato = ContatoSerializer().create(
                validated_data=contato_json)
            laboratorio.contatos.add(contato)

    def create(self, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        contatos = validated_data.pop('contatos', [])
        laboratorio = Laboratorio.objects.create(**validated_data)

        self.cria_contatos(contatos, laboratorio)
        return laboratorio

    def update(self, instance, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        contatos = validated_data.pop('contatos', [])

        instance.contatos.all().delete()

        self.cria_contatos(contatos, instance)
        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = Laboratorio
        exclude = ('id', )


class TipoEmbalagemQldCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=True)
    abreviacao = serializers.CharField(required=True)

    def create(self, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        validated_data['abreviacao'] = validated_data['abreviacao'].upper()
        embalagem = TipoEmbalagemQld.objects.create(**validated_data)

        return embalagem

    def update(self, instance, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        validated_data['abreviacao'] = validated_data['abreviacao'].upper()
        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = TipoEmbalagemQld
        exclude = ('id', )


def novo_numero_solicitacao(objeto):
    # Nova regra para sequência de numeração.
    objeto.numero_solicitacao = f'{str(objeto.pk).zfill(8)}-ALT'
    objeto.save()


class SolicitacaoDeAlteracaoCronogramaCreateSerializer(serializers.ModelSerializer):
    cronograma = serializers.UUIDField()
    etapas = serializers.JSONField(write_only=True)
    programacoes_de_recebimento = serializers.JSONField(write_only=True, required=False)

    def validate_cronograma(self, value):
        cronograma = Cronograma.objects.filter(uuid=value)
        if not cronograma:
            raise serializers.ValidationError(f'Cronograma não existe')
        if not cronograma.first().status == Cronograma.workflow_class.ASSINADO_CODAE:
            raise serializers.ValidationError(f'Não é possivel criar Solicitação de alteração neste momento!')
        return value

    def valida_campo_etapa(self, etapa, campo):
        if not etapa[campo]:
            raise serializers.ValidationError(
                {campo: ['Este campo é obrigatório.']}
            )

    def validate(self, attrs):
        for etapa in attrs['etapas']:
            self.valida_campo_etapa(etapa, 'etapa')
            self.valida_campo_etapa(etapa, 'parte')
            self.valida_campo_etapa(etapa, 'data_programada')
            self.valida_campo_etapa(etapa, 'quantidade')
            self.valida_campo_etapa(etapa, 'total_embalagens')
        return super().validate(attrs)

    def _criar_etapas(self, etapas):
        etapas_created = []
        for etapa in etapas:
            etapas_created.append(EtapasDoCronograma.objects.create(
                **etapa
            ))
        return etapas_created

    def create(self, validated_data):
        user = self.context['request'].user
        uuid_cronograma = validated_data.pop('cronograma', None)
        etapas = validated_data.pop('etapas', [])
        programacoes = validated_data.pop('programacoes_de_recebimento', [])
        cronograma = Cronograma.objects.get(uuid=uuid_cronograma)
        alteracao_cronograma = SolicitacaoAlteracaoCronograma.objects.create(
            usuario_solicitante=user,
            cronograma=cronograma, **validated_data,
        )
        alteracao_cronograma.etapas_antigas.set(cronograma.etapas.all())
        etapas_created = cria_etapas_de_cronograma(etapas)
        alteracao_cronograma.etapas_novas.set(etapas_created)
        programacoes_criadas = cria_programacao_de_cronograma(programacoes)
        alteracao_cronograma.programacoes_novas.set(programacoes_criadas)
        self._alterna_estado_cronograma(cronograma, user, alteracao_cronograma)
        self._alterna_estado_solicitacao_alteracao_cronograma(alteracao_cronograma, user, validated_data)
        return alteracao_cronograma

    def _alterna_estado_cronograma(self, cronograma, user, alteracao_cronograma):
        try:
            if user.eh_fornecedor:
                cronograma.fornecedor_solicita_alteracao(user=user, justificativa=alteracao_cronograma.uuid)
            else:
                cronograma.codae_realiza_alteracao(user=user, justificativa=alteracao_cronograma.uuid)
        except InvalidTransitionError as e:
            raise serializers.ValidationError(f'Erro de transição de estado do cronograma: {e}')

    def _alterna_estado_solicitacao_alteracao_cronograma(self, alteracao_cronograma, user, validated_data):
        try:
            if user.eh_fornecedor:
                alteracao_cronograma.inicia_fluxo(user=user, justificativa=validated_data.get('justificativa', ''))
            else:
                alteracao_cronograma.inicia_fluxo_codae(
                    user=user, justificativa=validated_data.get('justificativa', '')
                )
        except InvalidTransitionError as e:
            raise serializers.ValidationError(f'Erro de transição de estado da alteração: {e}')

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        exclude = ('id', 'usuario_solicitante', 'etapas_antigas', 'etapas_novas')


class UnidadeMedidaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ('uuid', 'nome', 'abreviacao', 'criado_em')
        read_only_fields = ('uuid', 'criado_em')

    def validate_nome(self, value):
        if not value.isupper():
            raise serializers.ValidationError('O campo deve conter apenas letras maiúsculas.')
        return value

    def validate_abreviacao(self, value):
        if not value.islower():
            raise serializers.ValidationError('O campo deve conter apenas letras minúsculas.')
        return value


class TipoDeEmbalagemDeLayoutCreateSerializer(serializers.ModelSerializer):
    tipo_embalagem = serializers.ChoiceField(
        choices=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_CHOICES, required=True, allow_blank=True)
    imagens_do_tipo_de_embalagem = serializers.JSONField(write_only=True)

    def validate(self, attrs):
        tipo_embalagem = attrs.get('tipo_embalagem', None)
        imagens = attrs.get('imagens_do_tipo_de_embalagem', None)

        if tipo_embalagem in [TipoDeEmbalagemDeLayout.PRIMARIA, TipoDeEmbalagemDeLayout.SECUNDARIA]:
            for img in imagens:
                if not img['arquivo'] or not img['nome']:
                    raise serializers.ValidationError(
                        {f'Layout de Embalagem {tipo_embalagem}': ['Este campo é obrigatório.']}
                    )
        return attrs

    class Meta:
        model = TipoDeEmbalagemDeLayout
        exclude = ('id', 'layout_de_embalagem')


class LayoutDeEmbalagemCreateSerializer(serializers.ModelSerializer):
    cronograma = serializers.UUIDField(required=True)
    tipos_de_embalagens = TipoDeEmbalagemDeLayoutCreateSerializer(many=True, required=False)
    observacoes = serializers.CharField(required=True)

    def validate_cronograma(self, value):
        cronograma = Cronograma.objects.filter(uuid=value)
        if not cronograma:
            raise serializers.ValidationError(f'Cronograma não existe')
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        uuid_cronograma = validated_data.pop('cronograma', None)
        tipos_de_embalagens = validated_data.pop('tipos_de_embalagens', [])
        cronograma = Cronograma.objects.get(uuid=uuid_cronograma)
        layout_de_embalagem = LayoutDeEmbalagem.objects.create(
            cronograma=cronograma, **validated_data,
        )
        cria_tipos_de_embalagens(tipos_de_embalagens, layout_de_embalagem)
        layout_de_embalagem.inicia_fluxo(user=user)

        return layout_de_embalagem

    class Meta:
        model = LayoutDeEmbalagem
        exclude = ('id',)
