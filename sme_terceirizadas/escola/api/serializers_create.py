from rest_framework import serializers

from ...dados_comuns.utils import update_instance_from_dict
from ...dieta_especial.models import TipoContagem
from ..models import (
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    FaixaEtaria,
    LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar,
    Lote,
    MudancaFaixasEtarias,
    PeriodoEscolar,
    Subprefeitura,
    TipoGestao
)


class LoteCreateSerializer(serializers.ModelSerializer):
    # TODO: calvin criar metodo create e update daqui. vide kit lanche para se basear
    diretoria_regional = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=DiretoriaRegional.objects.all()

    )
    subprefeituras = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Subprefeitura.objects.all()

    )
    tipo_gestao = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoGestao.objects.all()

    )

    escolas = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Escola.objects.all()
    )

    class Meta:
        model = Lote
        exclude = ('id',)


class EscolaPeriodoEscolarCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Escola.objects.all()
    )
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=PeriodoEscolar.objects.all()
    )
    quantidade_alunos = serializers.IntegerField()
    quantidade_alunos_anterior = serializers.IntegerField(required=False)
    justificativa = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        escola = validated_data.get('escola')
        periodo_escolar = validated_data.get('periodo_escolar')
        quantidade_alunos_para = validated_data.get('quantidade_alunos')
        quantidade_alunos_de = validated_data.pop('quantidade_alunos_anterior')
        justificativa = validated_data.pop('justificativa')
        criado_por = self.context['request'].user

        log = LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar(
            escola=escola,
            periodo_escolar=periodo_escolar,
            quantidade_alunos_para=quantidade_alunos_para,
            quantidade_alunos_de=quantidade_alunos_de,
            criado_por=criado_por,
            justificativa=justificativa
        )
        log.save()
        update_instance_from_dict(instance, validated_data, save=True)
        return instance

    class Meta:
        model = EscolaPeriodoEscolar
        exclude = ('id',)


class FaixaEtariaSerializer(serializers.ModelSerializer):
    __str__ = serializers.CharField()

    def validate(self, attrs):
        if attrs['inicio'] >= attrs['fim']:
            raise serializers.ValidationError(
                f"A faixa etária tem que terminar depois do início: inicio={attrs['inicio']};fim={attrs['fim']}"
            )
        return attrs

    class Meta:
        model = FaixaEtaria
        exclude = ('id', 'ativo')


class MudancaFaixasEtariasCreateSerializer(serializers.Serializer):
    justificativa = serializers.CharField()
    faixas_etarias_ativadas = FaixaEtariaSerializer(many=True)

    # TODO: Ver se é possível eliminar esse método ou pelo menos usar bulk_create
    def create(self, validated_data):
        FaixaEtaria.objects.update(ativo=False)
        faixas_etarias = validated_data.pop('faixas_etarias_ativadas', [])

        fe_objs = []
        for fe in faixas_etarias:
            ser = FaixaEtariaSerializer(data=fe)
            if ser.is_valid():
                fe_objs.append(ser.save())
            else:
                raise serializers.ValidationError('Erro ao salvar faixa etária: ' + ser.errors)

        mudanca = MudancaFaixasEtarias(justificativa=validated_data['justificativa'])
        mudanca.save()
        mudanca.faixas_etarias_ativadas.set(fe_objs)
        mudanca.save()
        return mudanca


class EscolaSimplesUpdateSerializer(serializers.ModelSerializer):
    tipos_contagem = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=TipoContagem.objects.all()
    )

    class Meta:
        model = Escola
        fields = ('tipos_contagem',)
