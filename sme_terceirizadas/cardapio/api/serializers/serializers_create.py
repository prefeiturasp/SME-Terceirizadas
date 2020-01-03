from rest_framework import serializers

from ....dados_comuns.utils import update_instance_from_dict
from ....dados_comuns.validators import (
    campo_nao_pode_ser_nulo,
    deve_existir_cardapio,
    deve_pedir_com_antecedencia,
    nao_pode_ser_feriado,
    nao_pode_ser_no_passado,
    objeto_nao_deve_ter_duplicidade
)
from ....escola.models import Escola, PeriodoEscolar, TipoUnidadeEscolar
from ....terceirizada.models import Edital
from ...api.validators import (
    data_troca_nao_pode_ser_superior_a_data_inversao,
    deve_ser_no_mesmo_ano_corrente,
    nao_pode_existir_solicitacao_igual_para_mesma_escola,
    nao_pode_ter_mais_que_60_dias_diferenca,
    precisa_pertencer_a_um_tipo_de_alimentacao
)
from ...models import (
    AlteracaoCardapio,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    GrupoSuspensaoAlimentacao,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicaoAlimentacaoNoPeriodoEscolar,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    SuspensaoAlimentacaoNoPeriodoEscolar,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)


class HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializerCreate(serializers.ModelSerializer):
    hora_inicial = serializers.TimeField()
    hora_final = serializers.TimeField()

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    combo_tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all()
    )

    class Meta:
        model = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar
        fields = ('uuid', 'hora_inicial', 'hora_final', 'escola', 'combo_tipos_alimentacao')


class InversaoCardapioSerializerCreate(serializers.ModelSerializer):
    data_de = serializers.DateField()
    data_para = serializers.DateField()

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def validate_data_de(self, data_de):
        deve_ser_no_mesmo_ano_corrente(data_de)
        nao_pode_ser_no_passado(data_de)
        return data_de

    def validate_data_para(self, data_para):
        deve_ser_no_mesmo_ano_corrente(data_para)
        nao_pode_ser_no_passado(data_para)
        return data_para

    def validate(self, attrs):
        data_de = attrs['data_de']
        data_para = attrs['data_para']
        escola = attrs['escola']

        data_troca_nao_pode_ser_superior_a_data_inversao(data_de, data_para)
        nao_pode_existir_solicitacao_igual_para_mesma_escola(data_de, data_para, escola)
        nao_pode_ter_mais_que_60_dias_diferenca(data_de, data_para)
        deve_existir_cardapio(escola, data_de)
        deve_existir_cardapio(escola, data_para)
        return attrs

    def create(self, validated_data):
        data_de = validated_data.pop('data_de')
        data_para = validated_data.pop('data_para')
        escola = validated_data.get('escola')

        validated_data['cardapio_de'] = escola.get_cardapio(data_de)
        validated_data['cardapio_para'] = escola.get_cardapio(data_para)
        validated_data['criado_por'] = self.context['request'].user

        inversao_cardapio = InversaoCardapio.objects.create(**validated_data)

        return inversao_cardapio

    def update(self, instance, validated_data):
        data_de = validated_data.pop('data_de')
        data_para = validated_data.pop('data_para')
        escola = validated_data.get('escola')
        validated_data['cardapio_de'] = escola.get_cardapio(data_de)
        validated_data['cardapio_para'] = escola.get_cardapio(data_para)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = InversaoCardapio
        fields = ('uuid', 'motivo', 'observacao', 'data_de', 'data_para', 'escola', 'status_explicacao')


class CardapioCreateSerializer(serializers.ModelSerializer):
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=True,
        queryset=TipoAlimentacao.objects.all()
    )
    edital = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Edital.objects.all()
    )

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        nao_pode_ser_feriado(data)
        objeto_nao_deve_ter_duplicidade(
            Cardapio,
            mensagem='Já existe um cardápio cadastrado com esta data',
            data=data
        )
        return data

    class Meta:
        model = Cardapio
        exclude = ('id',)


class SuspensaoAlimentacaoNoPeriodoEscolarCreateSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(slug_field='uuid',
                                                   queryset=PeriodoEscolar.objects.all())
    tipos_alimentacao = serializers.SlugRelatedField(slug_field='uuid',
                                                     many=True,
                                                     queryset=TipoAlimentacao.objects.all())

    class Meta:
        model = SuspensaoAlimentacaoNoPeriodoEscolar
        exclude = ('id', 'suspensao_alimentacao')


class SuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=MotivoSuspensao.objects.all()
    )

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        return data

    class Meta:
        model = SuspensaoAlimentacao
        exclude = ('id',)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all()
    )
    alteracao_cardapio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AlteracaoCardapio.objects.all()
    )

    tipo_alimentacao_de = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoAlimentacao.objects.all()
    )

    tipo_alimentacao_para = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoAlimentacao.objects.all()
    )

    def create(self, validated_data):
        substituicoes_alimentacao = SubstituicaoAlimentacaoNoPeriodoEscolar.objects.create(**validated_data)
        return substituicoes_alimentacao

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolar
        exclude = ('id',)


class AlteracaoCardapioSerializerCreate(serializers.ModelSerializer):
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(many=True)
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoAlteracaoCardapio.objects.all()
    )

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def validate_substituicoes(self, substituicoes):
        for substicuicao in substituicoes:
            tipo_alimentacao_de = substicuicao.get('tipo_alimentacao_de')
            tipo_alimentacao_para = substicuicao.get('tipo_alimentacao_para')
            precisa_pertencer_a_um_tipo_de_alimentacao(tipo_alimentacao_de, tipo_alimentacao_para)
        return substituicoes

    def validate_data_inicial(self, data_inicial):
        nao_pode_ser_no_passado(data_inicial)
        deve_pedir_com_antecedencia(data_inicial)
        return data_inicial

    def create(self, validated_data):
        substituicoes = validated_data.pop('substituicoes')
        validated_data['criado_por'] = self.context['request'].user

        substituicoes_lista = []
        for substituicao in substituicoes:
            substituicoes_object = SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(
            ).create(substituicao)
            substituicoes_lista.append(substituicoes_object)
        alteracao_cardapio = AlteracaoCardapio.objects.create(**validated_data)
        alteracao_cardapio.substituicoes.set(substituicoes_lista)

        return alteracao_cardapio

    def update(self, instance, validated_data):
        substituicoes_json = validated_data.pop('substituicoes')
        instance.substituicoes.all().delete()

        substituicoes_lista = []
        for substituicao_json in substituicoes_json:
            substituicoes_object = SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(
            ).create(substituicao_json)
            substituicoes_lista.append(substituicoes_object)

        update_instance_from_dict(instance, validated_data)
        instance.substituicoes.set(substituicoes_lista)
        instance.save()

        return instance

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id', 'status')


class QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=PeriodoEscolar.objects.all()
    )
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=TipoAlimentacao.objects.all()
    )

    class Meta:
        model = QuantidadePorPeriodoSuspensaoAlimentacao
        exclude = ('id', 'grupo_suspensao')


class GrupoSuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(slug_field='uuid',
                                          queryset=Escola.objects.all()
                                          )
    quantidades_por_periodo = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer(many=True)
    suspensoes_alimentacao = SuspensaoAlimentacaoCreateSerializer(many=True)

    def create(self, validated_data):
        quantidades_por_periodo_array = validated_data.pop('quantidades_por_periodo')
        suspensoes_alimentacao_array = validated_data.pop('suspensoes_alimentacao')
        validated_data['criado_por'] = self.context['request'].user

        quantidades = []
        for quantidade_json in quantidades_por_periodo_array:
            quantidade = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer().create(quantidade_json)
            quantidades.append(quantidade)

        suspensoes = []
        for suspensao_json in suspensoes_alimentacao_array:
            suspensao = SuspensaoAlimentacaoCreateSerializer().create(suspensao_json)
            suspensoes.append(suspensao)

        grupo = GrupoSuspensaoAlimentacao.objects.create(**validated_data)
        grupo.quantidades_por_periodo.set(quantidades)
        grupo.suspensoes_alimentacao.set(suspensoes)
        return grupo

    def update(self, instance, validated_data):
        quantidades_por_periodo_array = validated_data.pop('quantidades_por_periodo')
        suspensoes_alimentacao_array = validated_data.pop('suspensoes_alimentacao')

        instance.quantidades_por_periodo.all().delete()
        instance.suspensoes_alimentacao.all().delete()

        quantidades = []
        for quantidade_json in quantidades_por_periodo_array:
            quantidade = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer().create(quantidade_json)
            quantidades.append(quantidade)

        suspensoes = []
        for suspensao_json in suspensoes_alimentacao_array:
            suspensao = SuspensaoAlimentacaoCreateSerializer().create(suspensao_json)
            suspensoes.append(suspensao)

        update_instance_from_dict(instance, validated_data, save=True)
        instance.quantidades_por_periodo.set(quantidades)
        instance.suspensoes_alimentacao.set(suspensoes)

        return instance

    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ('id',)


class VinculoTipoAlimentoCreateSerializer(serializers.ModelSerializer):
    tipo_unidade_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all()
    )
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=PeriodoEscolar.objects.all()
    )

    tipos_alimentacao = serializers.SlugRelatedField(
        many=True,
        slug_field='uuid',
        queryset=TipoAlimentacao.objects.all()
    )

    def validate_tipos_alimentacao(self, tipos_alimentacao):
        campo_nao_pode_ser_nulo(tipos_alimentacao)
        return tipos_alimentacao

    class Meta:
        model = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
        fields = ('uuid', 'tipos_alimentacao', 'tipo_unidade_escolar', 'periodo_escolar')


class ComboDoVinculoTipoAlimentoSimplesSerializerCreate(serializers.ModelSerializer):
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        many=True,
        queryset=TipoAlimentacao.objects.all()
    )

    vinculo = serializers.SlugRelatedField(
        required=False,
        slug_field='uuid',
        queryset=VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all()
    )

    def validate_tipos_alimentacao(self, tipos_alimentacao):
        campo_nao_pode_ser_nulo(tipos_alimentacao, mensagem='tipos_alimentacao deve ter ao menos um elemento')
        return tipos_alimentacao

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'tipos_alimentacao', 'vinculo')


class SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializerCreate(serializers.ModelSerializer):
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        many=True,
        queryset=TipoAlimentacao.objects.all()
    )

    combo = serializers.SlugRelatedField(
        required=False,
        slug_field='uuid',
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all()
    )

    def validate_tipos_alimentacao(self, tipos_alimentacao):
        campo_nao_pode_ser_nulo(tipos_alimentacao, mensagem='tipos_alimentacao deve ter ao menos um elemento')
        return tipos_alimentacao

    class Meta:
        model = SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'tipos_alimentacao', 'combo')
