from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from workalendar.america import BrazilSaoPauloCity

from ....cardapio.models import ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
from ....dados_comuns.utils import update_instance_from_dict
from ....dados_comuns.validators import (
    deve_pedir_com_antecedencia,
    deve_ser_no_mesmo_ano_corrente,
    nao_pode_ser_no_passado
)
from ....escola.models import Escola, FaixaEtaria, PeriodoEscolar
from ...models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    InclusaoAlimentacaoNormal,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI,
    QuantidadePorPeriodo
)

calendario = BrazilSaoPauloCity()


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    faixa_etaria = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=FaixaEtaria.objects.all())

    def create(self, validated_data):
        quantidade_alunos_faixa_etaria = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI.objects.create(
            **validated_data
        )
        return quantidade_alunos_faixa_etaria

    class Meta:
        model = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI
        exclude = ('id', 'inclusao_alimentacao_da_cei',)


class InclusaoAlimentacaoDaCEICreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all())

    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all())

    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=True,
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all())

    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoNormal.objects.all())

    quantidade_alunos_por_faixas_etarias = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer(
        many=True,
        required=True
    )

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        deve_pedir_com_antecedencia(data)
        deve_ser_no_mesmo_ano_corrente(data)
        return data

    def create(self, validated_data):
        quantidade_alunos_por_faixas_etarias = validated_data.pop('quantidade_alunos_por_faixas_etarias')
        validated_data['criado_por'] = self.context['request'].user
        tipos_alimentacao = validated_data.pop('tipos_alimentacao')

        inclusao_alimentacao_da_cei = InclusaoAlimentacaoDaCEI.objects.create(**validated_data)
        inclusao_alimentacao_da_cei.tipos_alimentacao.set(tipos_alimentacao)
        for quantidade_json in quantidade_alunos_por_faixas_etarias:
            qtd = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer().create(
                validated_data=quantidade_json)
            inclusao_alimentacao_da_cei.adiciona_inclusao_a_quantidade_por_faixa_etaria(qtd)
        return inclusao_alimentacao_da_cei

    def update(self, instance, validated_data):
        quantidade_alunos_por_faixas_etarias = validated_data.pop('quantidade_alunos_por_faixas_etarias')
        tipos_alimentacao = validated_data.pop('tipos_alimentacao')

        instance.quantidade_alunos_da_inclusao.all().delete()
        instance.tipos_alimentacao.set([])
        instance.tipos_alimentacao.set(tipos_alimentacao)

        for quantidade_json in quantidade_alunos_por_faixas_etarias:
            qtd = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer().create(
                validated_data=quantidade_json)
            instance.adiciona_inclusao_a_quantidade_por_faixa_etaria(qtd)

        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = InclusaoAlimentacaoDaCEI
        exclude = ('id',)


class MotivoInclusaoContinuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoContinua
        exclude = ('id',)


class MotivoInclusaoNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoNormal
        exclude = ('id',)


class QuantidadePorPeriodoCreationSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all())

    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=True,
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all())

    grupo_inclusao_normal = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=GrupoInclusaoAlimentacaoNormal.objects.all())

    inclusao_alimentacao_continua = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=InclusaoAlimentacaoContinua.objects.all())

    def create(self, validated_data):
        tipos_alimentacao = validated_data.pop('tipos_alimentacao', [])
        quantidade_periodo = QuantidadePorPeriodo.objects.create(**validated_data)
        quantidade_periodo.tipos_alimentacao.set(tipos_alimentacao)
        return quantidade_periodo

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id',)


class InclusaoAlimentacaoNormalCreationSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoNormal.objects.all())

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        deve_pedir_com_antecedencia(data)
        return data

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)


class GrupoInclusaoAlimentacaoNormalCreationSerializer(serializers.ModelSerializer):
    inclusoes = InclusaoAlimentacaoNormalCreationSerializer(
        many=True,
        required=True
    )
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    quantidades_periodo = QuantidadePorPeriodoCreationSerializer(
        many=True,
        required=True
    )
    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def validate_quantidades_periodo(self, quantidades_periodo):
        if not quantidades_periodo:
            raise ValidationError('Deve possuir quantidades_periodo')
        return quantidades_periodo

    def create(self, validated_data):
        inclusoes_json = validated_data.pop('inclusoes')
        quantidades_periodo_json = validated_data.pop('quantidades_periodo')
        validated_data['criado_por'] = self.context['request'].user
        grupo_inclusao_alimentacao_normal = GrupoInclusaoAlimentacaoNormal.objects.create(**validated_data)

        for inclusao_json in inclusoes_json:
            inc = InclusaoAlimentacaoNormalCreationSerializer().create(
                validated_data=inclusao_json)
            grupo_inclusao_alimentacao_normal.adiciona_inclusao_normal(inc)

        for quantidade_periodo_json in quantidades_periodo_json:
            qtd = QuantidadePorPeriodoCreationSerializer().create(
                validated_data=quantidade_periodo_json)
            grupo_inclusao_alimentacao_normal.adiciona_quantidade_periodo(qtd)

        return grupo_inclusao_alimentacao_normal

    def update(self, instance, validated_data):
        inclusoes_json = validated_data.pop('inclusoes')
        quantidades_periodo_json = validated_data.pop('quantidades_periodo')
        instance.inclusoes.all().delete()
        instance.quantidades_periodo.all().delete()

        for inclusao_json in inclusoes_json:
            inc = InclusaoAlimentacaoNormalCreationSerializer().create(
                validated_data=inclusao_json)
            instance.adiciona_inclusao_normal(inc)

        for quantidade_periodo_json in quantidades_periodo_json:
            qtd = QuantidadePorPeriodoCreationSerializer().create(
                validated_data=quantidade_periodo_json)
            instance.adiciona_quantidade_periodo(qtd)

        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id', 'status')


class InclusaoAlimentacaoContinuaCreationSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoContinua.objects.all())
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    quantidades_periodo = QuantidadePorPeriodoCreationSerializer(many=True)
    dias_semana_explicacao = serializers.CharField(
        source='dias_semana_display',
        required=False,
        read_only=True
    )
    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def validate_data_inicial(self, data_inicial):
        nao_pode_ser_no_passado(data_inicial)
        deve_pedir_com_antecedencia(data_inicial)
        return data_inicial

    def validate_data_final(self, data_final):
        nao_pode_ser_no_passado(data_final)
        return data_final

    def validate_quantidades_periodo(self, quantidades_periodo):
        if not quantidades_periodo:
            raise ValidationError('Deve possuir quantidades_periodo')
        return quantidades_periodo

    def validate_feriados_no_periodo(self, data_inicial, data_final, dias_semana):
        # Valida se a faixa de datas não contém feriado
        # Não está sendo utilizado atualmente, cliente pediu para não validar
        data_atual = data_inicial
        while data_atual <= data_final:
            if dias_semana and data_atual.weekday() not in dias_semana:
                pass
            elif calendario.is_holiday(data_atual):
                data_formatada = data_atual.strftime('%d/%m/%Y')
                raise ValidationError(
                    f'Não pode haver feriado na faixa escolhida. Feriado encontrado: {data_formatada}')
            data_atual += timedelta(days=1)

    def validate(self, attrs):
        data_inicial = attrs.get('data_inicial', None)
        data_final = attrs.get('data_final', None)
        if data_inicial > data_final:
            raise ValidationError('data inicial não pode ser maior que data final')

        return attrs

    def create(self, validated_data):
        quantidades_periodo_array = validated_data.pop('quantidades_periodo')
        validated_data['criado_por'] = self.context['request'].user
        lista_escola_quantidade = self._gera_lista_escola_quantidade(quantidades_periodo_array)
        inclusao_alimentacao_continua = InclusaoAlimentacaoContinua.objects.create(
            **validated_data)
        inclusao_alimentacao_continua.quantidades_periodo.set(lista_escola_quantidade)

        return inclusao_alimentacao_continua

    def update(self, instance, validated_data):
        quantidades_periodo_array = validated_data.pop('quantidades_periodo')
        instance.quantidades_periodo.all().delete()
        lista_escola_quantidade = self._gera_lista_escola_quantidade(quantidades_periodo_array)
        instance.quantidades_periodo.set(lista_escola_quantidade)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    def _gera_lista_escola_quantidade(self, quantidades_periodo_array):
        escola_qtd_lista = []
        for quantidade_periodo_json in quantidades_periodo_array:
            quantidade_periodo = QuantidadePorPeriodoCreationSerializer(
            ).create(quantidade_periodo_json)
            escola_qtd_lista.append(quantidade_periodo)
        return escola_qtd_lista

    class Meta:
        model = InclusaoAlimentacaoContinua
        exclude = ('id', 'status')
