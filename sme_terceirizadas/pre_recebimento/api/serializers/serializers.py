import datetime
from collections import OrderedDict

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSimplesSerializer
from sme_terceirizadas.pre_recebimento.models import (
    AlteracaoCronogramaEtapa,
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    UnidadeMedida
)
from sme_terceirizadas.produto.api.serializers.serializers import NomeDeProdutoEditalSerializer, UnidadeMedidaSerialzer
from sme_terceirizadas.terceirizada.api.serializers.serializers import (
    ContratoSimplesSerializer,
    DistribuidorSimplesSerializer,
    TerceirizadaSimplesSerializer
)

from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer


class ProgramacaoDoRecebimentoDoCronogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        fields = ('uuid', 'data_programada', 'tipo_carga',)


class EtapasDoCronogramaSerializer(serializers.ModelSerializer):
    data_programada = serializers.SerializerMethodField()
    quantidade_atual = serializers.SerializerMethodField()
    data_programada_atual = serializers.SerializerMethodField()

    def get_data_programada(self, obj):
        return obj.data_programada.strftime('%d/%m/%Y') if obj.data_programada else None

    def get_quantidade_atual(self, obj):
        quantidade = obj.quantidade
        solicitacao_alteracao = obj.alteracaocronogramaetapa_set.filter(
            solicitacaoalteracaocronograma__status__in=['APROVADO_DILOG']).last()
        if solicitacao_alteracao:
            if solicitacao_alteracao.nova_quantidade:
                quantidade = solicitacao_alteracao.nova_quantidade
        return quantidade

    def get_data_programada_atual(self, obj):
        data = obj.data_programada
        solicitacao_alteracao = obj.alteracaocronogramaetapa_set.filter(
            solicitacaoalteracaocronograma__status__in=['APROVADO_DILOG']).last()
        if solicitacao_alteracao:
            if solicitacao_alteracao.nova_data_programada:
                data = solicitacao_alteracao.nova_data_programada
        return data.strftime('%d/%m/%Y') if data else None

    class Meta:
        model = EtapasDoCronograma
        fields = ('uuid', 'numero_empenho', 'etapa', 'parte', 'data_programada', 'quantidade',
                  'total_embalagens', 'quantidade_atual', 'data_programada_atual')


class SolicitacaoAlteracaoCronogramaSerializer(serializers.ModelSerializer):

    fornecedor = serializers.CharField(source='cronograma.empresa')
    cronograma = serializers.CharField(source='cronograma.numero')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ('uuid', 'numero_solicitacao', 'fornecedor', 'status', 'criado_em', 'cronograma')


class CronogramaSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(many=True)
    armazem = DistribuidorSimplesSerializer()
    status = serializers.CharField(source='get_status_display')
    empresa = TerceirizadaSimplesSerializer()
    contrato = ContratoSimplesSerializer()
    produto = NomeDeProdutoEditalSerializer()
    unidade_medida = UnidadeMedidaSerialzer()

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'criado_em', 'alterado_em', 'contrato', 'empresa',
                          'produto', 'qtd_total_programada', 'unidade_medida',
                          'tipo_embalagem', 'armazem', 'etapas', 'programacoes_de_recebimento')


class CronogramaComLogSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(many=True)
    armazem = DistribuidorSimplesSerializer()
    status = serializers.CharField(source='get_status_display')
    empresa = TerceirizadaSimplesSerializer()
    contrato = ContratoSimplesSerializer()
    produto = NomeDeProdutoEditalSerializer()
    unidade_medida = UnidadeMedidaSerialzer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'criado_em', 'alterado_em', 'contrato', 'empresa',
                          'produto', 'qtd_total_programada', 'unidade_medida',
                          'tipo_embalagem', 'armazem', 'etapas', 'programacoes_de_recebimento', 'logs')


class SolicitacaoAlteracaoCronogramaEtapaSerializer(serializers.ModelSerializer):
    etapa = serializers.CharField(source='etapa.uuid')

    class Meta:
        model = AlteracaoCronogramaEtapa
        fields = '__all__'


class SolicitacaoAlteracaoCronogramaCompletoSerializer(serializers.ModelSerializer):

    fornecedor = serializers.CharField(source='cronograma.empresa')
    cronograma = CronogramaSerializer()
    status = serializers.CharField(source='get_status_display')
    etapas = SolicitacaoAlteracaoCronogramaEtapaSerializer(many=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ('uuid', 'numero_solicitacao', 'fornecedor', 'status', 'criado_em', 'cronograma',
                  'motivo', 'etapas', 'justificativa', 'logs')


class CronogramaRascunhosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'alterado_em')


class PainelCronogramaSerializer(serializers.ModelSerializer):
    produto = serializers.SerializerMethodField()
    empresa = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    def get_produto(self, obj):
        return obj.produto.nome if obj.produto else None

    def get_empresa(self, obj):
        return obj.empresa.razao_social if obj.empresa else None

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'status', 'empresa', 'produto', 'log_mais_recente')


class PainelSolicitacaoAlteracaoCronogramaSerializerItem(serializers.ModelSerializer):

    empresa = serializers.CharField(source='cronograma.empresa')
    cronograma = serializers.CharField(source='cronograma.numero')
    status = serializers.CharField(source='get_status_display')
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_criado_em:
            if obj.log_criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.log_criado_em, '%d/%m/%Y')

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ('uuid', 'numero_solicitacao', 'empresa', 'status', 'cronograma', 'log_mais_recente')


class PainelSolicitacaoAlteracaoCronogramaSerializer(serializers.Serializer):
    status = serializers.CharField()
    dados = serializers.SerializerMethodField()
    total = serializers.IntegerField(allow_null=True)

    def get_dados(self, obj):
        return PainelSolicitacaoAlteracaoCronogramaSerializerItem(obj['dados'], many=True).data

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ('uuid', 'status', 'total', 'dados')

    def to_representation(self, instance):
        result = super(PainelSolicitacaoAlteracaoCronogramaSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class LaboratorioSerializer(serializers.ModelSerializer):

    contatos = ContatoSimplesSerializer(many=True)

    class Meta:
        model = Laboratorio
        exclude = ('id', )


class LaboratorioSimplesFiltroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ('nome', 'cnpj')
        read_only_fields = ('nome', 'cnpj')


class EmbalagemQldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbalagemQld
        exclude = ('id', )


class UnidadeMedidaSerialzer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ('uuid', 'nome', 'abreviacao', 'criado_em')
        read_only_fields = ('uuid', 'nome', 'abreviacao', 'criado_em')


class NomeEAbreviacaoUnidadeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ('nome', 'abreviacao')
        read_only_fields = ('nome', 'abreviacao')
