from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import fields, serializers
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.logistica.api.helpers import (
    registra_conferencias_individuais,
    verifica_se_a_guia_pode_ser_conferida
)
from sme_terceirizadas.logistica.models import (
    Alimento,
    ConferenciaGuia,
    Guia,
    NotificacaoOcorrenciasGuia,
    PrevisaoContratualNotificacao,
    SolicitacaoDeAlteracaoRequisicao,
    SolicitacaoRemessa
)
from sme_terceirizadas.logistica.models.guia import ConferenciaIndividualPorAlimento, InsucessoEntregaGuia
from sme_terceirizadas.logistica.services import exclui_ultima_reposicao
from sme_terceirizadas.perfil.api.serializers import UsuarioVinculoSerializer
from sme_terceirizadas.terceirizada.models import Terceirizada


class AlimentoCreateSerializer(serializers.Serializer):
    StrCodSup = serializers.CharField()
    StrCodPapa = serializers.CharField()
    StrNomAli = serializers.CharField()
    StrEmbala = serializers.CharField()
    IntQtdVol = serializers.CharField()

    def create(self, validated_data):
        return Alimento.objects.create_alimento(**validated_data)


class GuiaCreateSerializer(serializers.Serializer):
    StrNumGui = serializers.CharField()
    DtEntrega = serializers.DateField()
    StrCodUni = serializers.CharField()
    StrNomUni = serializers.CharField()
    StrEndUni = serializers.CharField()
    StrNumUni = serializers.CharField()
    StrBaiUni = serializers.CharField()
    StrCepUni = serializers.CharField()
    StrCidUni = serializers.CharField()
    StrEstUni = serializers.CharField()
    StrConUni = serializers.CharField()
    StrTelUni = serializers.CharField()
    alimentos = AlimentoCreateSerializer(many=True)

    def create(self, validated_data):
        alimentos = validated_data.pop('alimentos', [])
        guia = Guia.objects.create_guia(**validated_data)
        for alimento_json in alimentos:
            alimento_json['guia'] = guia
            AlimentoCreateSerializer().create(validated_data=alimento_json)
        return guia


class SolicitacaoRemessaCreateSerializer(serializers.Serializer):
    StrCnpj = serializers.CharField(max_length=14)
    StrNumSol = serializers.CharField(max_length=30)
    guias = GuiaCreateSerializer(many=True)

    def create(self, validated_data):
        guias = validated_data.pop('guias', [])
        validated_data.pop('IntSeqenv', None)
        validated_data.pop('IntQtGuia', None)
        validated_data.pop('IntTotVol', None)
        cnpj = validated_data.get('StrCnpj', None)
        try:
            distribuidor = Terceirizada.objects.get(cnpj=cnpj)
            validated_data['distribuidor'] = distribuidor
        except ObjectDoesNotExist:
            pass

        solicitacao = SolicitacaoRemessa.objects.create_solicitacao(**validated_data)
        for guia_json in guias:
            guia_json['solicitacao'] = solicitacao
            GuiaCreateSerializer().create(validated_data=guia_json)
        return solicitacao


def novo_numero_solicitacao(objeto):
    # Nova regra para sequência de numeração.
    objeto.numero_solicitacao = f'{str(objeto.pk).zfill(8)}-ALT'
    objeto.save()


class SolicitacaoDeAlteracaoRequisicaoCreateSerializer(serializers.ModelSerializer):
    motivo = fields.MultipleChoiceField(choices=SolicitacaoDeAlteracaoRequisicao.MOTIVO_CHOICES)
    requisicao = serializers.UUIDField()

    def create(self, validated_data):  # noqa C901
        user = self.context['request'].user
        uuid_requisicao = validated_data.pop('requisicao', None)
        try:
            requisicao = SolicitacaoRemessa.objects.get(uuid=uuid_requisicao)

            dias_uteis = self.get_diferenca_dias_uteis(requisicao.guias.first().data_entrega)

            if dias_uteis <= 3:
                raise serializers.ValidationError(
                    'Data limite alcançada. Não é mais possível alterar essa requisição.')

            solicitacao_alteracao = SolicitacaoDeAlteracaoRequisicao.objects.create(
                usuario_solicitante=user,
                requisicao=requisicao, **validated_data
            )
            novo_numero_solicitacao(solicitacao_alteracao)
            try:
                requisicao.solicita_alteracao(user=user, justificativa=validated_data.get('justificativa', ''))
                solicitacao_alteracao.inicia_fluxo(user=user, justificativa=validated_data.get('justificativa', ''))
            except InvalidTransitionError as e:
                raise serializers.ValidationError(f'Erro de transição de estado: {e}')
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'Requisição de remessa não existe.')

        return solicitacao_alteracao

    def get_diferenca_dias_uteis(self, data_entrega):
        hoje = datetime.now().date()
        cal_dias = 1 + ((data_entrega - hoje).days * 5 - (hoje.weekday() - data_entrega.weekday()) * 2) / 7

        if hoje.weekday() == 5:
            cal_dias = cal_dias - 1
        if data_entrega.weekday() == 6:
            cal_dias = cal_dias - 1

        return cal_dias

    class Meta:
        model = SolicitacaoDeAlteracaoRequisicao
        exclude = ('id', 'usuario_solicitante')


class ConferenciaDaGuiaCreateSerializer(serializers.ModelSerializer):
    guia = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Guia.objects.all()
    )
    nome_motorista = serializers.CharField(required=True)
    placa_veiculo = serializers.CharField(required=True)
    data_recebimento = serializers.DateField(required=True)
    hora_recebimento = serializers.TimeField(required=True)
    criado_por = UsuarioVinculoSerializer(required=False)

    class Meta:
        model = ConferenciaGuia
        exclude = ('id',)

    def create(self, validated_data):  # noqa C901
        guia_request = validated_data.get('guia', None)
        user = self.context['request'].user
        validated_data['criado_por'] = user
        try:
            guia = Guia.objects.get(uuid=guia_request.uuid)
            conferencia_guia = ConferenciaGuia.objects.create(**validated_data)
            try:
                guia.escola_recebe(user=user)
            except InvalidTransitionError as e:
                raise serializers.ValidationError(f'Erro de transição de estado: {e}')
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'Guia de remessa não existe.')

        return conferencia_guia


class ConferenciaIndividualPorAlimentoCreateSerializer(serializers.ModelSerializer):
    conferencia = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ConferenciaGuia.objects.all()
    )
    tipo_embalagem = serializers.ChoiceField(
        choices=ConferenciaIndividualPorAlimento.TIPO_EMBALAGEM_CHOICES, required=True)
    nome_alimento = serializers.CharField(required=True)
    qtd_recebido = serializers.IntegerField(required=True)
    status_alimento = serializers.ChoiceField(
        choices=ConferenciaIndividualPorAlimento.STATUS_ALIMENTO_CHOICES, required=True)
    ocorrencia = fields.MultipleChoiceField(choices=ConferenciaIndividualPorAlimento.OCORRENCIA_CHOICES, required=True)

    class Meta:
        model = ConferenciaIndividualPorAlimento
        exclude = ('id',)


class ConferenciaComOcorrenciaCreateSerializer(serializers.ModelSerializer):
    conferencia_dos_alimentos = ConferenciaIndividualPorAlimentoCreateSerializer(many=True, required=False)
    guia = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Guia.objects.all()
    )
    nome_motorista = serializers.CharField(required=True)
    placa_veiculo = serializers.CharField(required=True)
    data_recebimento = serializers.DateField(required=True)
    hora_recebimento = serializers.TimeField(required=True)
    criado_por = UsuarioVinculoSerializer(required=False)

    class Meta:
        model = ConferenciaGuia
        exclude = ('id',)

    def create(self, validated_data): # noqa C901
        guia_request = validated_data.get('guia', None)
        try:
            guia = Guia.objects.get(uuid=guia_request.uuid)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'Guia de remessa não existe.')
        eh_reposicao = validated_data.get('eh_reposicao', False)
        verifica_se_a_guia_pode_ser_conferida(guia)
        user = self.context['request'].user
        validated_data['criado_por'] = user
        conferencia_dos_alimentos = validated_data.pop('conferencia_dos_alimentos')
        conferencia_guia = ConferenciaGuia.objects.create(**validated_data)
        registra_conferencias_individuais(guia, conferencia_guia, conferencia_dos_alimentos, user, eh_reposicao)

        return conferencia_guia

    def update(self, instance, validated_data): # noqa C901
        guia_request = validated_data.get('guia', None)
        try:
            guia = Guia.objects.get(uuid=guia_request.uuid)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'Guia de remessa não existe.')
        conferencia_dos_alimentos = validated_data.pop('conferencia_dos_alimentos')
        eh_reposicao = validated_data.get('eh_reposicao', False)
        user = self.context['request'].user
        validated_data['criado_por'] = user

        verifica_se_a_guia_pode_ser_conferida(guia)
        if guia.situacao == Guia.ARQUIVADA:
            raise serializers.ValidationError(
                'Não é possível realizar a edição de uma conferencia/reposição de uma guia arquivada.')
        elif eh_reposicao and not conferencia_dos_alimentos:
            raise serializers.ValidationError('Uma reposição deve conter ao menos uma conferência individual.')
        elif not eh_reposicao:
            exclui_ultima_reposicao(guia)

        instance.conferencia_dos_alimentos.all().delete()
        update_instance_from_dict(instance, validated_data, save=True)

        if conferencia_dos_alimentos:
            registra_conferencias_individuais(
                guia, instance, conferencia_dos_alimentos, user, eh_reposicao, edicao=True)
        else:
            try:
                guia.escola_recebe(user=user)
            except InvalidTransitionError as e:
                raise serializers.ValidationError(f'Erro de transição de estado: {e}')

        return instance


class InsucessoDeEntregaGuiaCreateSerializer(serializers.ModelSerializer):
    guia = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Guia.objects.all()
    )
    motivo = serializers.CharField(required=True)
    nome_motorista = serializers.CharField(required=True)
    placa_veiculo = serializers.CharField(required=True)
    hora_tentativa = serializers.TimeField(required=True)
    justificativa = serializers.CharField(required=True)
    criado_por = UsuarioVinculoSerializer(required=False)

    class Meta:
        model = InsucessoEntregaGuia
        exclude = ('id',)

    def create(self, validated_data):  # noqa C901
        guia_request = validated_data.get('guia', None)
        user = self.context['request'].user
        validated_data['criado_por'] = user
        try:
            guia = Guia.objects.get(uuid=guia_request.uuid)
            insucesso_entrega = InsucessoEntregaGuia.objects.create(**validated_data)
            try:
                guia.distribuidor_registra_insucesso(user=user)
            except InvalidTransitionError as e:
                raise serializers.ValidationError(f'Erro de transição de estado: {e}')
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'Guia de remessa não existe.')

        return insucesso_entrega


class PrevisoesContratuaisDaNotificacaoCreateSerializer(serializers.ModelSerializer):
    previsao_contratual = serializers.CharField(required=False, allow_blank=True)
    tipo_ocorrencia = serializers.ChoiceField(
        choices=ConferenciaIndividualPorAlimento.OCORRENCIA_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = PrevisaoContratualNotificacao
        exclude = ('id', 'notificacao')


class NotificacaoOcorrenciasCreateSerializer(serializers.ModelSerializer):
    empresa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Terceirizada.objects.filter(tipo_servico=Terceirizada.DISTRIBUIDOR_ARMAZEM)
    )

    guias = serializers.ListField(required=False)
    processo_sei = serializers.CharField(required=False)
    link_processo_sei = serializers.URLField(required=False)
    previsoes = PrevisoesContratuaisDaNotificacaoCreateSerializer(many=True, required=False)

    def gera_proximo_numero_notificacao(self):
        ano = date.today().year
        ultima_notificacao = NotificacaoOcorrenciasGuia.objects.last()
        if ultima_notificacao:
            return f'{str(int(ultima_notificacao.numero[:3]) + 1).zfill(3)}/{ano}'
        else:
            return f'001/{ano}'

    def vincula_guias_a_notificacao(self, guias, notificacao):
        Guia.objects.filter(uuid__in=guias).update(notificacao=notificacao)

    def cria_previsoes(self, previsoes, notificacao):
        for previsao in previsoes:
            PrevisaoContratualNotificacao.objects.create(
                notificacao=notificacao,
                **previsao
            )

    def validate(self, attrs):
        guias = attrs.get('guias', None)
        if not guias:
            raise serializers.ValidationError(
                {'guias': ['Este campo é obrigatório.']}
            )
        existe_guia_notificada = Guia.objects.filter(uuid__in=guias, notificacao__isnull=False)

        instance = getattr(self, 'instance', None)

        if instance:
            guias_atuais = set(instance.guias_notificadas.all())
            guias_novas = set(existe_guia_notificada)
            existe_guia_notificada = list(guias_novas - guias_atuais)

        if existe_guia_notificada:
            raise serializers.ValidationError(
                {'guias': ['Existem uma ou mais guias que já estão notificadas.']}
            )
        return attrs

    def create(self, validated_data):
        previsoes = validated_data.pop('previsoes', [])
        guias = validated_data.pop('guias', [])
        numero_notificacao = self.gera_proximo_numero_notificacao()
        notificacao = NotificacaoOcorrenciasGuia.objects.create(numero=numero_notificacao, **validated_data)

        self.vincula_guias_a_notificacao(guias, notificacao)
        self.cria_previsoes(previsoes, notificacao)

        return notificacao
    
    class Meta:
        model = NotificacaoOcorrenciasGuia
        exclude = ('id', )


class NotificacaoOcorrenciasUpdateRascunhoSerializer(serializers.ModelSerializer):
    def vincula_guias_a_notificacao(self, guias, notificacao):
        Guia.objects.filter(uuid__in=guias).update(notificacao=notificacao)

    def desvincula_guias_a_notificacao(self, guias):
        Guia.objects.filter(uuid__in=guias).update(notificacao=None)

    def validate(self, attrs, instance):
        guias = attrs.get('guias', None)
        if not guias:
            raise serializers.ValidationError(
                {'guias': ['Este campo é obrigatório.']}
            )
        existe_guia_notificada = Guia.objects.filter(uuid__in=guias, notificacao__isnull=False)

        guias_atuais = set(instance.guias_notificadas.all())
        guias_novas = set(existe_guia_notificada)
        existe_guia_notificada = list(guias_novas - guias_atuais)

        if existe_guia_notificada:
            raise serializers.ValidationError(
                {'guias': ['Existem uma ou mais guias que já estão notificadas.']}
            )
        return attrs

    def update(self, instance, validated_data):
        guias = validated_data.pop('guias', [])

        guias_notificadas = [guia.uuid for guia in instance.guias_notificadas.all()]
        self.desvincula_guias_a_notificacao(guias_notificadas)
        self.vincula_guias_a_notificacao(guias, instance)

        return instance

    class Meta:
        model = NotificacaoOcorrenciasGuia
        exclude = ('id', )
