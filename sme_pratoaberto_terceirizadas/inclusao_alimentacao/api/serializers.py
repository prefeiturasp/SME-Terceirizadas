from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import InclusaoAlimentacao, DescricaoInclusaoAlimentacao, \
    MotivoInclusaoAlimentacao, DiaMotivoInclusaoAlimentacao


class MotivoInclusaoAlimentacaoSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    valor = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.nome

    def get_value(self, obj):
        return obj.nome

    class Meta:
        model = MotivoInclusaoAlimentacao
        fields = ('label', 'valor')


class DiaMotivoInclusaoAlimentacaoSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    do_dia = serializers.SerializerMethodField()
    ate_dia = serializers.SerializerMethodField()
    dias_semana = serializers.SerializerMethodField()
    motivo = serializers.SerializerMethodField()

    def obter_dia(self, obj):
        return obj.data.strftime('%d/%m/%Y') if obj.data else None

    def obter_do_dia(self, obj):
        return obj.do_dia.strftime('%d/%m/%Y') if obj.do_dia else None

    def obter_ate_dia(self, obj):
        return obj.ate_dia.strftime('%d/%m/%Y') if obj.ate_dia else None

    def obter_dias_semana(self, obj):
        if obj.dias_semana:
            if isinstance(obj.dias_semana, list):
                return obj.dias_semana
            else:
                return [day for day in obj.dias_semana.split(',')]
        return None

    def obter_motivo(self, obj):
        return obj.motivo.nome

    class Meta:
        model = DiaMotivoInclusaoAlimentacao
        fields = ('id', 'data', 'do_dia', 'ate_dia', 'dias_semana', 'qual_motivo', 'prioridade', 'motivo')


class DescricaoInclusaoAlimentacaoSerializer(serializers.ModelSerializer):
    verifica = serializers.SerializerMethodField()
    valor = serializers.SerializerMethodField()
    select = serializers.SerializerMethodField()
    numero = serializers.SerializerMethodField()

    def obter_verificacao(self, obj):
        return True

    def obter_valor(self, obj):
        return obj.periodo.valor

    def obter_select(self, obj):
        return [refeicao.nome for refeicao in obj.tipo_refeicao.all()]

    def obter_numero(self, obj):
        return str(obj.numero_de_estudantes)

    class Meta:
        model = DescricaoInclusaoAlimentacao
        fields = ('verifica', 'valor', 'select', 'numero')


class InclusaoAlimentacaoSerializer(serializers.ModelSerializer):
    descricao_primeiro_periodo = serializers.SerializerMethodField()
    descricao_segundo_periodo = serializers.SerializerMethodField()
    descricao_terceiro_periodo = serializers.SerializerMethodField()
    descricao_quarto_periodo = serializers.SerializerMethodField()
    descricao_integral = serializers.SerializerMethodField()
    criado_em = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    motivos_dia = serializers.SerializerMethodField()

    # TODO: verificar o que é "period__value"

    def obter_descricao_primeiro_periodo(self, obj):
        if obj.descricoes.filter(period__value=PeriodoEscolar.PRIMEIRO_PERIODO).exists():
            return DescricaoInclusaoAlimentacaoSerializer(obj.descricoes.get(
                period__value=PeriodoEscolar.PRIMEIRO_PERIODO)).data
        return None

    def obter_descricao_segundo_periodo(self, obj):
        if obj.descricoes.filter(period__value=PeriodoEscolar.SEGUNDO_PERIODO).exists():
            return DescricaoInclusaoAlimentacaoSerializer(obj.descricoes.get(
                period__value=PeriodoEscolar.SEGUNDO_PERIODO)).data
        return None

    def obter_descricao_terceiro_periodo(self, obj):
        if obj.descricoes.filter(period__value=PeriodoEscolar.TERCEIRO_PERIODO).exists():
            return DescricaoInclusaoAlimentacaoSerializer(obj.descricoes.get(
                period__value=PeriodoEscolar.TERCEIRO_PERIODO)).data
        return None

    def obter_descricao_quarto_periodo(self, obj):
        if obj.descricoes.filter(period__value=PeriodoEscolar.QUARTO_PERIODO).exists():
            return DescricaoInclusaoAlimentacaoSerializer(obj.descricoes.get(
                period__value=PeriodoEscolar.QUARTO_PERIODO)).data
        return None

    def obter_descricao_integral(self, obj):
        if obj.descricoes.filter(period__value=PeriodoEscolar.INTEGRAL).exists():
            return DescricaoInclusaoAlimentacaoSerializer(obj.descricoes.get(
                period__value=PeriodoEscolar.INTEGRAL)).data
        return None

    def obter_motivos_dia(self, obj):
        if obj.motivos.exists():
            return DiaMotivoInclusaoAlimentacaoSerializer(
                obj.motivos.all(), many=True).data
        return None

    def obter_criado_em(self, obj):
        return obj.created_at.strftime("%d/%m/%Y às %H:%M")

    def obter_status(self, obj):
        return obj.status.nome if obj.status else None

    # TODO: verificar fields do class Meta

    class Meta:
        model = InclusaoAlimentacao
        fields = (
            'id', 'uuid', 'created_at', 'descricao_primeiro_periodo', 'descricao_segundo_periodo',
            'descricao_terceiro_periodo', 'descricao_quarto_periodo', 'descricao_integral',
            'status', 'obs', 'motivos_dia')
