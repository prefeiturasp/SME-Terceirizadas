from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import fields, serializers
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSerializer
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.pre_recebimento.models import (
    AlteracaoCronogramaEtapa,
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma
)
from sme_terceirizadas.terceirizada.models import Terceirizada


class ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(serializers.ModelSerializer):
    data_programada = serializers.CharField(required=False)
    tipo_carga = serializers.ChoiceField(
        choices=ProgramacaoDoRecebimentoDoCronograma.TIPO_CARGA_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        exclude = ('id', 'cronograma')


class EtapasDoCronogramaCreateSerializer(serializers.ModelSerializer):
    empenho_uuid = serializers.UUIDField(required=False)
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
        queryset=Terceirizada.objects.all(),
        allow_null=True
    )
    contrato_uuid = serializers.UUIDField(required=True)
    contrato = serializers.CharField(required=True)
    empresa_uuid = serializers.UUIDField(required=False)
    nome_empresa = serializers.CharField(required=False)
    produto_uuid = serializers.UUIDField(required=False)
    processo_sei = serializers.CharField(required=False)
    nome_produto = serializers.CharField(required=False)
    qtd_total_programada = serializers.FloatField(required=False)
    unidade_medida = serializers.CharField(required=False)
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

    def cria_etapas(self, etapas, cronograma):
        for etapa in etapas:
            EtapasDoCronograma.objects.create(
                cronograma=cronograma,
                **etapa
            )

    def cria_programacao(self, programacoes, cronograma):
        for programacao in programacoes:
            ProgramacaoDoRecebimentoDoCronograma.objects.create(
                cronograma=cronograma,
                **programacao
            )

    def create(self, validated_data):
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])
        numero_cronograma = self.gera_proximo_numero_cronograma()
        cronograma = Cronograma.objects.create(numero=numero_cronograma, **validated_data)
        cronograma.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_CRIADO, usuario=user)

        self.cria_etapas(etapas, cronograma)
        self.cria_programacao(programacoes_de_recebimento, cronograma)

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

        self.cria_etapas(etapas, instance)
        self.cria_programacao(programacoes_de_recebimento, instance)

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


class EmbalagemQldCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=True)
    abreviacao = serializers.CharField(required=True)

    def create(self, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        validated_data['abreviacao'] = validated_data['abreviacao'].upper()
        embalagem = EmbalagemQld.objects.create(**validated_data)

        return embalagem

    def update(self, instance, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        validated_data['abreviacao'] = validated_data['abreviacao'].upper()
        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = EmbalagemQld
        exclude = ('id', )


def novo_numero_solicitacao(objeto):
    # Nova regra para sequência de numeração.
    objeto.numero_solicitacao = f'{str(objeto.pk).zfill(8)}-ALT'
    objeto.save()


class SolicitacaoDeAlteracaoCronogramaCreateSerializer(serializers.ModelSerializer):
    motivo = fields.MultipleChoiceField(choices=SolicitacaoAlteracaoCronograma.MOTIVO_CHOICES)
    cronograma = serializers.UUIDField()
    etapas = serializers.JSONField(write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        uuid_cronograma = validated_data.pop('cronograma', None)
        etapas = validated_data.pop('etapas', [])
        try:
            cronograma = Cronograma.objects.get(uuid=uuid_cronograma)
            etapas_create = []
            for etapa in etapas:
                etapas_create.append(AlteracaoCronogramaEtapa.objects.create(
                    etapa=EtapasDoCronograma.objects.get(uuid=etapa['uuid']),
                    nova_data_programada=etapa['nova_data_programada']
                ))
            alteracao_cronograma = SolicitacaoAlteracaoCronograma.objects.create(
                usuario_solicitante=user,
                cronograma=cronograma, **validated_data,
            )
            novo_numero_solicitacao(alteracao_cronograma)
            alteracao_cronograma.etapas.set(etapas_create)
            try:
                cronograma.solicita_alteracao(user=user, justificativa=validated_data.get('justificativa', ''))
                alteracao_cronograma.inicia_fluxo(user=user, justificativa=validated_data.get('justificativa', ''))
            except InvalidTransitionError as e:
                raise serializers.ValidationError(f'Erro de transição de estado: {e}')
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(f'Cronograma não existe: {e}')
        return alteracao_cronograma

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        exclude = ('id', 'usuario_solicitante')
