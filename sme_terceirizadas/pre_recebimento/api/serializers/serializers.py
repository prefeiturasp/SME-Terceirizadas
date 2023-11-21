import datetime
from collections import OrderedDict

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSimplesSerializer
from sme_terceirizadas.pre_recebimento.models import (
    ArquivoDoTipoDeDocumento,
    Cronograma,
    DataDeFabricaoEPrazo,
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

    def get_data_programada(self, obj):
        return obj.data_programada.strftime('%d/%m/%Y') if obj.data_programada else None

    class Meta:
        model = EtapasDoCronograma
        fields = ('uuid', 'numero_empenho', 'etapa', 'parte', 'data_programada', 'quantidade',
                  'total_embalagens')


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


class SolicitacaoAlteracaoCronogramaCompletoSerializer(serializers.ModelSerializer):

    fornecedor = serializers.CharField(source='cronograma.empresa')
    cronograma = CronogramaSerializer()
    status = serializers.CharField(source='get_status_display')
    etapas_antigas = EtapasDoCronogramaSerializer(many=True)
    etapas_novas = EtapasDoCronogramaSerializer(many=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ('uuid', 'numero_solicitacao', 'fornecedor', 'status', 'criado_em', 'cronograma',
                  'etapas_antigas', 'etapas_novas', 'justificativa', 'logs')


class CronogramaRascunhosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'alterado_em')


class CronogramaSimplesSerializer(serializers.ModelSerializer):
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()

    def get_pregao_chamada_publica(self, obj):
        return obj.contrato.pregao_chamada_publica if obj.contrato else None

    def get_nome_produto(self, obj):
        return obj.produto.nome if obj.produto else None

    class Meta:
        model = Cronograma
        fields = ('uuid', 'numero', 'pregao_chamada_publica', 'nome_produto')


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


class LaboratorioCredenciadoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ('uuid', 'nome')
        read_only_fields = ('uuid', 'nome')


class TipoEmbalagemQldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEmbalagemQld
        exclude = ('id', )


class UnidadeMedidaSerialzer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ('uuid', 'nome', 'abreviacao', 'criado_em')
        read_only_fields = ('uuid', 'nome', 'abreviacao', 'criado_em')


class NomeEAbreviacaoUnidadeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ('uuid', 'nome', 'abreviacao')
        read_only_fields = ('uuid', 'nome', 'abreviacao')


class ImagemDoTipoEmbalagemLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImagemDoTipoDeEmbalagem
        exclude = ('id', 'uuid', 'tipo_de_embalagem')


class TipoEmbalagemLayoutLookupSerializer(serializers.ModelSerializer):
    imagens = ImagemDoTipoEmbalagemLookupSerializer(many=True)

    class Meta:
        model = TipoDeEmbalagemDeLayout
        exclude = ('id', 'layout_de_embalagem')


class LayoutDeEmbalagemSerializer(serializers.ModelSerializer):
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return obj.cronograma.contrato.pregao_chamada_publica if obj.cronograma.contrato else None

    def get_nome_produto(self, obj):
        return obj.cronograma.produto.nome if obj.cronograma.produto else None

    class Meta:
        model = LayoutDeEmbalagem
        fields = ('uuid', 'numero_cronograma', 'pregao_chamada_publica', 'nome_produto', 'status', 'criado_em')


class LayoutDeEmbalagemDetalheSerializer(serializers.ModelSerializer):
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    nome_empresa = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')
    tipos_de_embalagens = TipoEmbalagemLayoutLookupSerializer(many=True)
    log_mais_recente = serializers.SerializerMethodField()
    primeira_analise = serializers.SerializerMethodField()

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return obj.cronograma.contrato.pregao_chamada_publica if obj.cronograma.contrato else None

    def get_nome_produto(self, obj):
        return obj.cronograma.produto.nome if obj.cronograma.produto else None

    def get_nome_empresa(self, obj):
        return obj.cronograma.empresa.razao_social if obj.cronograma.empresa else None

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y - %H:%M')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y - %H:%M')

    def get_primeira_analise(self, obj):
        return obj.eh_primeira_analise

    class Meta:
        model = LayoutDeEmbalagem
        fields = (
            'uuid', 'observacoes', 'criado_em', 'status', 'tipos_de_embalagens',
            'numero_cronograma', 'pregao_chamada_publica', 'nome_produto', 'nome_empresa',
            'log_mais_recente', 'primeira_analise'
        )


class PainelLayoutEmbalagemSerializer(serializers.ModelSerializer):
    numero_cronograma = serializers.CharField(source='cronograma.numero')
    nome_produto = serializers.CharField(source='cronograma.produto')
    nome_empresa = serializers.CharField(source='cronograma.empresa.razao_social')
    status = serializers.CharField(source='get_status_display')
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    class Meta:
        model = LayoutDeEmbalagem
        fields = ('uuid', 'numero_cronograma', 'nome_produto', 'nome_empresa', 'status', 'log_mais_recente')


class DocumentoDeRecebimentoSerializer(serializers.ModelSerializer):
    criado_em = serializers.SerializerMethodField()
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return obj.cronograma.contrato.pregao_chamada_publica if obj.cronograma.contrato else None

    def get_nome_produto(self, obj):
        return obj.cronograma.produto.nome if obj.cronograma.produto else None

    def get_criado_em(self, obj):
        return obj.criado_em.strftime('%d/%m/%Y')

    class Meta:
        model = DocumentoDeRecebimento
        fields = ('uuid', 'numero_cronograma', 'pregao_chamada_publica', 'nome_produto', 'status', 'criado_em')


class PainelDocumentoDeRecebimentoSerializer(serializers.ModelSerializer):
    numero_cronograma = serializers.CharField(source='cronograma.numero')
    nome_produto = serializers.CharField(source='cronograma.produto')
    nome_empresa = serializers.CharField(source='cronograma.empresa.razao_social')
    status = serializers.CharField(source='get_status_display')
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    class Meta:
        model = DocumentoDeRecebimento
        fields = ('uuid', 'numero_cronograma', 'nome_produto', 'nome_empresa', 'status', 'log_mais_recente')


class ArquivoDoTipoDeDocumentoLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArquivoDoTipoDeDocumento
        exclude = ('id', 'uuid', 'tipo_de_documento')


class TipoDocumentoDeRecebimentoLookupSerializer(serializers.ModelSerializer):
    arquivos = ArquivoDoTipoDeDocumentoLookupSerializer(many=True)

    class Meta:
        model = TipoDeDocumentoDeRecebimento
        exclude = ('id', 'documento_recebimento')


class DocRecebimentoDetalharSerializer(serializers.ModelSerializer):
    criado_em = serializers.SerializerMethodField()
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')
    tipos_de_documentos = TipoDocumentoDeRecebimentoLookupSerializer(many=True)

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return obj.cronograma.contrato.pregao_chamada_publica if obj.cronograma.contrato else None

    def get_nome_produto(self, obj):
        return obj.cronograma.produto.nome if obj.cronograma.produto else None

    def get_criado_em(self, obj):
        return obj.criado_em.strftime('%d/%m/%Y')

    class Meta:
        model = DocumentoDeRecebimento
        fields = ('uuid', 'numero_cronograma', 'pregao_chamada_publica', 'nome_produto', 'numero_laudo', 'status',
                  'criado_em', 'tipos_de_documentos', 'correcao_solicitada',)


class DataDeFabricacaoEPrazoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeFabricaoEPrazo
        exclude = ('id', 'documento_recebimento')


class DocRecebimentoDetalharCodaeSerializer(DocRecebimentoDetalharSerializer):
    laboratorio = serializers.UUIDField(source='laboratorio.uuid', read_only=True)
    unidade_medida = serializers.UUIDField(source='unidade_medida.uuid', read_only=True)
    datas_fabricacao_e_prazos = DataDeFabricacaoEPrazoLookupSerializer(many=True)
    numero_sei = serializers.SerializerMethodField()
    fornecedor = serializers.SerializerMethodField()

    def get_numero_sei(self, obj):
        return obj.cronograma.contrato.processo if obj.cronograma.contrato else None

    def get_fornecedor(self, obj):
        return obj.cronograma.empresa.nome_fantasia if obj.cronograma.empresa else None

    class Meta(DocRecebimentoDetalharSerializer.Meta):
        fields = DocRecebimentoDetalharSerializer.Meta.fields + ('fornecedor', 'numero_sei', 'laboratorio',
                                                                 'quantidade_laudo', 'unidade_medida', 'saldo_laudo',
                                                                 'data_fabricacao_lote', 'validade_produto',
                                                                 'data_final_lote', 'datas_fabricacao_e_prazos',)
