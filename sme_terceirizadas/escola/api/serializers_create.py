from rest_framework import serializers
from ...dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.perfil.models import Usuario

from ..models import (
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar,
    Lote,
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
    quantidade_alunos_atual = serializers.IntegerField(required=False)
    justificativa = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        escola = validated_data.get('escola')
        periodo_escolar = validated_data.get('periodo_escolar')
        quantidade_alunos_alterada = validated_data.get('quantidade_alunos')
        quantidade_alunos_atual = validated_data.pop('quantidade_alunos_atual')
        justificativa = validated_data.pop('justificativa')
        criado_por = self.context['request'].user

        log = LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar(
            escola=escola,
            periodo_escolar=periodo_escolar,
            quantidade_alunos_alterada=quantidade_alunos_alterada,
            quantidade_alunos_atual=quantidade_alunos_atual,
            criado_por=criado_por,
            justificativa=justificativa
        )
        log.save()
        update_instance_from_dict(instance, validated_data, save=True)
        return instance

    class Meta:
        model = EscolaPeriodoEscolar
        exclude = ('id',)
