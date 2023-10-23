from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSerializer
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    DocumentoDeRecebimento,
    EtapasDoCronograma,
    ImagemDoTipoDeEmbalagem,
    Laboratorio,
    LayoutDeEmbalagem,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    TipoDeDocumentoDeRecebimento,
    TipoDeEmbalagemDeLayout,
    TipoEmbalagemQld,
    UnidadeMedida
)
from sme_terceirizadas.produto.models import NomeDeProdutoEdital
from sme_terceirizadas.terceirizada.models import Contrato, Terceirizada

from ..helpers import (
    cria_etapas_de_cronograma,
    cria_programacao_de_cronograma,
    cria_tipos_de_documentos,
    cria_tipos_de_embalagens
)
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
        tipos_obrigatorios = [
            TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA,
            TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA
        ]

        if tipo_embalagem in tipos_obrigatorios:
            for img in imagens:
                if not img['arquivo'] or not img['nome']:
                    raise serializers.ValidationError(
                        {f'Layout Embalagem {tipo_embalagem}': ['Este campo é obrigatório.']}
                    )
        return attrs

    class Meta:
        model = TipoDeEmbalagemDeLayout
        exclude = ('id', 'layout_de_embalagem')


class LayoutDeEmbalagemCreateSerializer(serializers.ModelSerializer):
    cronograma = serializers.UUIDField(required=False)
    tipos_de_embalagens = TipoDeEmbalagemDeLayoutCreateSerializer(many=True, required=False)
    observacoes = serializers.CharField(required=False)

    def validate_cronograma(self, value):
        if value is not None:
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

    def update(self, instance, validated_data):
        try:
            user = self.context['request'].user
            dados_correcao = validated_data.pop('tipos_de_embalagens', [])

            instance.tipos_de_embalagens.all().delete()
            cria_tipos_de_embalagens(dados_correcao, instance)

            instance.observacoes = validated_data.pop('observacoes', '')
            instance.fornecedor_atualiza(user=user)
            instance.save()

        except InvalidTransitionError as e:
            raise serializers.ValidationError(
                f'Erro de transição de estado. O status deste layout não permite correção: {e}')

        return instance

    class Meta:
        model = LayoutDeEmbalagem
        exclude = ('id',)


class TipoDeEmbalagemDeLayoutAnaliseSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()

    def validate(self, attrs):
        uuid = attrs.get('uuid', None)
        tipo_embalagem = attrs.get('tipo_embalagem', None)
        embalagem = TipoDeEmbalagemDeLayout.objects.filter(uuid=uuid).last()

        if not embalagem:
            raise serializers.ValidationError({f'Layout Embalagem {tipo_embalagem}': [
                'UUID do tipo informado não existe.'
            ]})

        if (
            not embalagem.layout_de_embalagem.eh_primeira_analise and
            embalagem.status != TipoDeEmbalagemDeLayout.STATUS_EM_ANALISE
        ):
            raise serializers.ValidationError({f'Layout Embalagem {tipo_embalagem}': [
                'O Tipo/UUID informado não pode ser analisado pois não está em análise.'
            ]})

        return attrs

    class Meta:
        model = TipoDeEmbalagemDeLayout
        fields = ('uuid', 'tipo_embalagem', 'status', 'complemento_do_status')
        extra_kwargs = {
            'uuid': {'required': True},
            'tipo_embalagem': {'required': True},
            'status': {'required': True},
            'complemento_do_status': {'required': True},
        }


class LayoutDeEmbalagemAnaliseSerializer(serializers.ModelSerializer):
    tipos_de_embalagens = TipoDeEmbalagemDeLayoutAnaliseSerializer(many=True)

    def validate_tipos_de_embalagens(self, value):
        self._validar_primeira_analise(value)
        self._validar_analise_correcao(value)

        return value

    def _validar_primeira_analise(self, value):
        if self.instance.eh_primeira_analise:
            if not len(value) == self.instance.tipos_de_embalagens.count():
                raise serializers.ValidationError(
                    'Quantidade de Tipos de Embalagem recebida para primeira análise ' +
                    'é diferente da quantidade presente no Layout de Embalagem.'
                )

    def _validar_analise_correcao(self, value):
        if not self.instance.eh_primeira_analise:
            if not len(value) == self.instance.tipos_de_embalagens.filter(status='EM_ANALISE').count():
                raise serializers.ValidationError(
                    'Quantidade de Tipos de Embalagem recebida para análise da correção' +
                    ' é diferente da quantidade em análise.'
                )

    def update(self, instance, validated_data):
        try:
            user = self.context['request'].user
            dados_tipos_de_embalagens = validated_data.pop('tipos_de_embalagens', [])

            for dados in dados_tipos_de_embalagens:
                tipo_de_embalagem = instance.tipos_de_embalagens.get(uuid=dados['uuid'])
                tipo_de_embalagem.status = dados['status']
                tipo_de_embalagem.complemento_do_status = dados['complemento_do_status']
                tipo_de_embalagem.save()

            instance.codae_aprova(user=user) if instance.aprovado else instance.codae_solicita_correcao(user=user)

        except InvalidTransitionError as e:
            raise serializers.ValidationError(
                f'Erro de transição de estado. O status deste layout não permite analise: {e}')

        return instance

    class Meta:
        model = LayoutDeEmbalagem
        fields = ('tipos_de_embalagens',)


class TipoDeEmbalagemDeLayoutCorrecaoSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()
    tipo_embalagem = serializers.ChoiceField(
        choices=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_CHOICES, required=True, allow_blank=True)
    imagens_do_tipo_de_embalagem = serializers.JSONField(write_only=True, required=True)

    def validate(self, attrs):
        uuid = attrs.get('uuid', None)
        tipo = attrs.get('tipo_embalagem', None)
        imagens = attrs.get('imagens_do_tipo_de_embalagem', None)
        embalagem = TipoDeEmbalagemDeLayout.objects.filter(uuid=uuid).last()

        if not embalagem:
            raise serializers.ValidationError(
                {f'Layout Embalagem {tipo}': ['UUID do tipo informado não existe.']}
            )
        if embalagem.status != TipoDeEmbalagemDeLayout.STATUS_REPROVADO:
            raise serializers.ValidationError(
                {f'Layout Embalagem {tipo}': ['O Tipo/UUID informado não pode ser corrigido pois não está reprovado.']}
            )
        for img in imagens:
            if not img['arquivo'] or not img['nome']:
                raise serializers.ValidationError(
                    {f'Layout Embalagem {tipo}': ['arquivo/nome é obrigatório.']}
                )
        return attrs

    class Meta:
        model = TipoDeEmbalagemDeLayout
        exclude = ('id', 'layout_de_embalagem')


class LayoutDeEmbalagemCorrecaoSerializer(serializers.ModelSerializer):
    tipos_de_embalagens = TipoDeEmbalagemDeLayoutCorrecaoSerializer(many=True, required=True)
    observacoes = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        try:
            user = self.context['request'].user
            dados_correcao = validated_data.pop('tipos_de_embalagens', [])

            for embalagem in dados_correcao:
                tipo_embalagem = instance.tipos_de_embalagens.get(uuid=embalagem['uuid'])
                tipo_embalagem.status = TipoDeEmbalagemDeLayout.STATUS_EM_ANALISE
                tipo_embalagem.imagens.all().delete()
                tipo_embalagem.save()
                imagens = embalagem.pop('imagens_do_tipo_de_embalagem', [])
                for img in imagens:
                    data = convert_base64_to_contentfile(img.get('arquivo'))
                    ImagemDoTipoDeEmbalagem.objects.create(
                        tipo_de_embalagem=tipo_embalagem, arquivo=data, nome=img.get('nome', '')
                    )

            instance.observacoes = validated_data.pop('observacoes', '')
            instance.fornecedor_realiza_correcao(user=user)
            instance.save()

        except InvalidTransitionError as e:
            raise serializers.ValidationError(
                f'Erro de transição de estado. O status deste layout não permite correção: {e}')

        return instance

    class Meta:
        model = LayoutDeEmbalagem
        fields = ('tipos_de_embalagens', 'observacoes')


class TipoDeDocumentoDeRecebimentoCreateSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.ChoiceField(
        choices=TipoDeDocumentoDeRecebimento.TIPO_DOC_CHOICES, required=True, allow_blank=False)
    arquivos_do_tipo_de_documento = serializers.JSONField(write_only=True)
    descricao_documento = serializers.CharField(required=False)

    def validate(self, attrs):
        tipo_documento = attrs.get('tipo_documento', None)
        arquivos = attrs.get('arquivos_do_tipo_de_documento', None)
        tipos_obrigatorios = [
            TipoDeDocumentoDeRecebimento.TIPO_DOC_LAUDO,
        ]

        if tipo_documento in tipos_obrigatorios:
            for doc in arquivos:
                if not doc['arquivo'] or not doc['nome']:
                    raise serializers.ValidationError(
                        {f'{tipo_documento}': ['Este campo é obrigatório.']}
                    )
        return attrs

    class Meta:
        model = TipoDeDocumentoDeRecebimento
        exclude = ('id', 'documento_recebimento')


class DocumentoDeRecebimentoCreateSerializer(serializers.ModelSerializer):
    cronograma = serializers.UUIDField(required=True)
    tipos_de_documentos = TipoDeDocumentoDeRecebimentoCreateSerializer(many=True, required=False)
    numero_laudo = serializers.CharField(required=True)

    def validate_cronograma(self, value):
        cronograma = Cronograma.objects.filter(uuid=value)
        if not cronograma:
            raise serializers.ValidationError(f'Cronograma não existe')
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        uuid_cronograma = validated_data.pop('cronograma', None)
        tipos_de_documentos = validated_data.pop('tipos_de_documentos', [])
        cronograma = Cronograma.objects.get(uuid=uuid_cronograma)
        documento_de_recebimento = DocumentoDeRecebimento.objects.create(
            cronograma=cronograma, **validated_data,
        )
        cria_tipos_de_documentos(tipos_de_documentos, documento_de_recebimento)
        documento_de_recebimento.inicia_fluxo(user=user)

        return documento_de_recebimento

    class Meta:
        model = DocumentoDeRecebimento
        exclude = ('id',)
