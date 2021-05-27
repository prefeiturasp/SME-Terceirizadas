from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import fields, serializers
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.logistica.models import (
    Alimento,
    ConferenciaGuia,
    Guia,
    SolicitacaoDeAlteracaoRequisicao,
    SolicitacaoRemessa
)
from sme_terceirizadas.logistica.models.guia import ConferenciaIndividualPorAlimento, InsucessoEntregaGuia
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
    ocorrencia = fields.MultipleChoiceField(choices=ConferenciaIndividualPorAlimento.OCORRENCIA_CHOICES, required=False)

    def create(self, validated_data):
        ocorrencia = validated_data.get('ocorrencia', None)
        if ocorrencia:
            validated_data['tem_ocorrencia'] = True
        conferencia_individual = ConferenciaIndividualPorAlimento.objects.create(**validated_data)
        return conferencia_individual

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
        user = self.context['request'].user
        validated_data['criado_por'] = user
        conferencia_dos_alimentos_list = []
        conferencia_dos_alimentos = validated_data.pop('conferencia_dos_alimentos')
        conferencia_guia = ConferenciaGuia.objects.create(**validated_data)
        for alimento in conferencia_dos_alimentos:
            alimento['conferencia'] = conferencia_guia
            conferencia_individual = ConferenciaIndividualPorAlimentoCreateSerializer().create(alimento)
            conferencia_dos_alimentos_list.append(conferencia_individual)
        conferencia_guia.conferencia_dos_alimentos.set(conferencia_dos_alimentos_list)

        return conferencia_guia


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
