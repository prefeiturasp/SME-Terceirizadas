from rest_framework import serializers

from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....dados_comuns.utils import update_instance_from_dict
from ....escola.api.serializers import (
    AlunoSerializer,
    AlunoSimplesSerializer,
    DiretoriaRegionalSimplissimaSerializer,
    EscolaSimplesSerializer,
    FaixaEtariaSerializer
)
from ....escola.models import FaixaEtaria
from ....terceirizada.api.serializers.serializers import EditalSerializer, TerceirizadaSimplesSerializer
from ....terceirizada.models import Edital
from ...models import (
    EscolaQuantidade,
    FaixaEtariaSolicitacaoKitLancheCEIAvulsa,
    FaixasQuantidadesKitLancheCEIdaCEMEI,
    ItemKitLanche,
    KitLanche,
    SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa,
    SolicitacaoKitLancheCEIAvulsa,
    SolicitacaoKitLancheCEIdaCEMEI,
    SolicitacaoKitLancheCEMEI,
    SolicitacaoKitLancheEMEIdaCEMEI,
    SolicitacaoKitLancheUnificada
)


class ItemKitLancheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemKitLanche
        exclude = ('id',)


class KitLancheSerializer(serializers.ModelSerializer):
    edital = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Edital.objects.all()
    )

    class Meta:
        model = KitLanche
        exclude = ('id',)

    def validate_nome_kit_lanche_create(self, validated_data):
        if (KitLanche.objects.filter(edital__uuid=validated_data['edital'].uuid,
                                     nome=validated_data['nome'].upper()).first()):
            raise serializers.ValidationError('Esse nome de kit lanche já existe para edital selecionado')
        validated_data['nome'] = validated_data['nome'].upper()
        return validated_data

    def validate_nome_kit_lanche_update(self, validated_data, instance):
        if (KitLanche.objects.filter(
            edital__uuid=validated_data['edital'].uuid,
                nome=validated_data['nome'].upper()).exclude(uuid=str(instance.uuid)).first()):
            serializers.ValidationError('Esse nome de kit lanche já existe para edital selecionado')
        validated_data['nome'] = validated_data['nome'].upper()
        return validated_data

    def create(self, validated_data):
        self.validate_nome_kit_lanche_create(validated_data)
        kit_lanche = KitLanche.objects.create(**validated_data)
        return kit_lanche

    def update(self, instance, validated_data):
        self.validate_nome_kit_lanche_update(validated_data, instance)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance


class KitLancheSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitLanche
        exclude = ('id',)


class KitLancheConsultaSerializer(serializers.ModelSerializer):
    edital = EditalSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = KitLanche
        exclude = ('id',)


class SolicitacaoKitLancheSimplesSerializer(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = SolicitacaoKitLanche
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaSimilarSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    data = serializers.DateField()

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escola = EscolaSimplesSerializer(read_only=True,
                                     required=False)
    prioridade = serializers.CharField()
    id_externo = serializers.CharField()
    alunos_com_dieta_especial_participantes = AlunoSerializer(many=True)
    foi_solicitado_fora_do_prazo = serializers.BooleanField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    quantidade_alimentacoes = serializers.IntegerField()
    data = serializers.DateField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    solicitacoes_similares = SolicitacaoKitLancheAvulsaSimilarSerializer(many=True)

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()
    id_externo = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id', 'solicitacao_kit_lanche', 'escola', 'criado_por')


class EscolaQuantidadeSerializerSimples(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    escola = EscolaSimplesSerializer()
    solicitacao_unificada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=SolicitacaoKitLancheUnificada.objects.all())
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaSimilarSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escolas_quantidades = EscolaQuantidadeSerializerSimples(many=True)
    id_externo = serializers.CharField()
    # TODO: remover total_kit_lanche ou quantidade_alimentacoes. estao duplicados
    total_kit_lanche = serializers.IntegerField()
    lote_nome = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    data = serializers.DateField()
    quantidade_alimentacoes = serializers.IntegerField()

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escolas_quantidades = EscolaQuantidadeSerializerSimples(many=True)
    id_externo = serializers.CharField()
    # TODO: remover total_kit_lanche ou quantidade_alimentacoes. estao duplicados
    total_kit_lanche = serializers.IntegerField()
    lote_nome = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()
    data = serializers.DateField()
    quantidade_alimentacoes = serializers.IntegerField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    solicitacoes_similares = SolicitacaoKitLancheUnificadaSimilarSerializer(many=True)

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class EscolaQuantidadeSerializer(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    escola = EscolaSimplesSerializer()

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)


class FaixaEtariaSolicitacaoKitLancheCEIAvulsaSerializer(serializers.ModelSerializer):
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = FaixaEtariaSolicitacaoKitLancheCEIAvulsa
        exclude = ('id', 'solicitacao_kit_lanche_avulsa')


class SolicitacaoKitLancheCEIAvulsaSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    faixas_etarias = FaixaEtariaSolicitacaoKitLancheCEIAvulsaSerializer(many=True)
    quantidade_alunos = serializers.IntegerField()
    id_externo = serializers.CharField()
    alunos_com_dieta_especial_participantes = AlunoSerializer(many=True)
    prioridade = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    escola = EscolaSimplesSerializer()
    solicitacoes_similares = SolicitacaoKitLancheAvulsaSimilarSerializer(many=True)

    def to_representation(self, instance):
        retorno = super().to_representation(instance)

        # Inclui o total de alunos nas faixas etárias
        faixas_etarias_da_solicitacao = FaixaEtaria.objects.filter(
            uuid__in=[f.faixa_etaria.uuid for f in instance.faixas_etarias.all()]
        )

        qtde_alunos = instance.escola.alunos_por_faixa_etaria(instance.data, faixas_etarias_da_solicitacao)
        for faixa_etaria in retorno['faixas_etarias']:
            uuid_faixa_etaria = faixa_etaria['faixa_etaria']['uuid']
            faixa_etaria['total_alunos_no_periodo'] = qtde_alunos[uuid_faixa_etaria]

        return retorno

    class Meta:
        model = SolicitacaoKitLancheCEIAvulsa
        exclude = ('id', 'criado_por')


class FaixasQuantidadesKitLancheCEIdaCEMEISerializer(serializers.ModelSerializer):
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = FaixasQuantidadesKitLancheCEIdaCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheCEIdaCEMEISerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='uuid')
    alunos_com_dieta_especial_participantes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='uuid')
    faixas_quantidades = FaixasQuantidadesKitLancheCEIdaCEMEISerializer(many=True)
    tempo_passeio = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheCEIdaCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheEMEIdaCEMEISerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='uuid')
    alunos_com_dieta_especial_participantes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='uuid')
    tempo_passeio = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheEMEIdaCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheCEMEISimilarSerializer(serializers.ModelSerializer):
    solicitacao_cei = SolicitacaoKitLancheCEIdaCEMEISerializer()
    solicitacao_emei = SolicitacaoKitLancheEMEIdaCEMEISerializer()
    id_externo = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheCEMEISerializer(serializers.ModelSerializer):
    solicitacao_cei = SolicitacaoKitLancheCEIdaCEMEISerializer()
    solicitacao_emei = SolicitacaoKitLancheEMEIdaCEMEISerializer()
    solicitacoes_similares = SolicitacaoKitLancheCEMEISimilarSerializer(many=True)
    id_externo = serializers.CharField()
    escola = serializers.UUIDField(source='escola.uuid')

    class Meta:
        model = SolicitacaoKitLancheCEMEI
        exclude = ('id',)


class KitLancheNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitLanche
        fields = ('nome',)


class SolicitacaoKitLancheEMEIdaCEMEIRetrieveSerializer(serializers.ModelSerializer):
    alunos_com_dieta_especial_participantes = AlunoSimplesSerializer(many=True)
    kits = KitLancheNomeSerializer(many=True)
    tempo_passeio = serializers.CharField()
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = SolicitacaoKitLancheEMEIdaCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheCEIdaCEMEIRetrieveSerializer(serializers.ModelSerializer):
    alunos_com_dieta_especial_participantes = AlunoSimplesSerializer(many=True)
    kits = KitLancheNomeSerializer(many=True)
    faixas_quantidades = FaixasQuantidadesKitLancheCEIdaCEMEISerializer(many=True)
    tempo_passeio = serializers.CharField()
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = SolicitacaoKitLancheCEIdaCEMEI
        exclude = ('id',)


class SolicitacaoKitLancheCEMEIRetrieveSerializer(serializers.ModelSerializer):
    solicitacao_cei = SolicitacaoKitLancheCEIdaCEMEIRetrieveSerializer()
    solicitacao_emei = SolicitacaoKitLancheEMEIdaCEMEIRetrieveSerializer()
    id_externo = serializers.CharField()
    escola = EscolaSimplesSerializer()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    prioridade = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    data = serializers.DateField()

    class Meta:
        model = SolicitacaoKitLancheCEMEI
        exclude = ('id',)
