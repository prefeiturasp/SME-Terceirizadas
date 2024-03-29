import datetime
from collections import OrderedDict

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSimplesSerializer
from sme_terceirizadas.pre_recebimento.models import (
    AnaliseFichaTecnica,
    ArquivoDoTipoDeDocumento,
    Cronograma,
    DataDeFabricaoEPrazo,
    DocumentoDeRecebimento,
    EtapasDoCronograma,
    ImagemDoTipoDeEmbalagem,
    InformacoesNutricionaisFichaTecnica,
    Laboratorio,
    LayoutDeEmbalagem,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    TipoDeDocumentoDeRecebimento,
    TipoDeEmbalagemDeLayout,
    TipoEmbalagemQld,
    UnidadeMedida,
)
from sme_terceirizadas.produto.api.serializers.serializers import (
    FabricanteSimplesSerializer,
    InformacaoNutricionalSerializer,
    MarcaSimplesSerializer,
    NomeDeProdutoEditalSerializer,
    UnidadeMedidaSerialzer,
)
from sme_terceirizadas.terceirizada.api.serializers.serializers import (
    ContratoSimplesSerializer,
    DistribuidorComEnderecoSimplesSerializer,
    DistribuidorSimplesSerializer,
    TerceirizadaLookUpSerializer,
    TerceirizadaSimplesSerializer,
)

from ....dados_comuns.api.serializers import (
    LogSolicitacoesUsuarioSerializer,
    LogSolicitacoesUsuarioSimplesSerializer,
)
from ...models.cronograma import FichaTecnicaDoProduto


class ProgramacaoDoRecebimentoDoCronogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        fields = (
            "uuid",
            "data_programada",
            "tipo_carga",
        )


class EtapasDoCronogramaSerializer(serializers.ModelSerializer):
    data_programada = serializers.SerializerMethodField()

    def get_data_programada(self, obj):
        return obj.data_programada.strftime("%d/%m/%Y") if obj.data_programada else None

    class Meta:
        model = EtapasDoCronograma
        fields = (
            "uuid",
            "numero_empenho",
            "qtd_total_empenho",
            "etapa",
            "parte",
            "data_programada",
            "quantidade",
            "total_embalagens",
        )


class EtapasDoCronogramaCalendarioSerializer(serializers.ModelSerializer):
    nome_produto = serializers.SerializerMethodField()
    uuid_cronograma = serializers.SerializerMethodField()
    numero_cronograma = serializers.SerializerMethodField()
    nome_fornecedor = serializers.SerializerMethodField()
    data_programada = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_nome_produto(self, obj):
        try:
            return obj.cronograma.ficha_tecnica.produto.nome
        except AttributeError:
            return None

    def get_uuid_cronograma(self, obj):
        return obj.cronograma.uuid if obj.cronograma else None

    def get_numero_cronograma(self, obj):
        return str(obj.cronograma.numero) if obj.cronograma else None

    def get_nome_fornecedor(self, obj):
        return obj.cronograma.empresa.nome_fantasia if obj.cronograma.empresa else None

    def get_data_programada(self, obj):
        return obj.data_programada.strftime("%d/%m/%Y") if obj.data_programada else None

    def get_status(self, obj):
        return obj.cronograma.get_status_display() if obj.cronograma else None

    class Meta:
        model = EtapasDoCronograma
        fields = (
            "uuid",
            "nome_produto",
            "uuid_cronograma",
            "numero_cronograma",
            "nome_fornecedor",
            "data_programada",
            "numero_empenho",
            "etapa",
            "parte",
            "quantidade",
            "status",
        )


class SolicitacaoAlteracaoCronogramaSerializer(serializers.ModelSerializer):
    fornecedor = serializers.CharField(source="cronograma.empresa")
    cronograma = serializers.CharField(source="cronograma.numero")
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = (
            "uuid",
            "numero_solicitacao",
            "fornecedor",
            "status",
            "criado_em",
            "cronograma",
        )


class TipoEmbalagemQldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEmbalagemQld
        exclude = ("id",)


class NomeEAbreviacaoUnidadeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ("uuid", "nome", "abreviacao")
        read_only_fields = ("uuid", "nome", "abreviacao")


class FichaTecnicaSimplesSerializer(serializers.ModelSerializer):
    produto = NomeDeProdutoEditalSerializer()
    uuid_empresa = serializers.SerializerMethodField()

    def get_uuid_empresa(self, obj):
        return obj.empresa.uuid if obj.empresa else None

    class Meta:
        model = FichaTecnicaDoProduto
        fields = (
            "uuid",
            "numero",
            "produto",
            "uuid_empresa",
            "pregao_chamada_publica",
        )


class FichaTecnicaCronogramaSerializer(FichaTecnicaSimplesSerializer):
    marca = MarcaSimplesSerializer()
    unidade_medida_volume_primaria = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_primaria = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_secundaria = NomeEAbreviacaoUnidadeMedidaSerializer()

    class Meta(FichaTecnicaSimplesSerializer.Meta):
        fields = FichaTecnicaSimplesSerializer.Meta.fields + (
            "marca",
            "volume_embalagem_primaria",
            "unidade_medida_volume_primaria",
            "peso_liquido_embalagem_primaria",
            "unidade_medida_primaria",
            "peso_liquido_embalagem_secundaria",
            "unidade_medida_secundaria",
        )


class CronogramaSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(
        many=True
    )
    armazem = DistribuidorSimplesSerializer()
    status = serializers.CharField(source="get_status_display")
    empresa = TerceirizadaSimplesSerializer()
    contrato = ContratoSimplesSerializer()
    unidade_medida = UnidadeMedidaSerialzer()
    ficha_tecnica = FichaTecnicaCronogramaSerializer()

    class Meta:
        model = Cronograma
        fields = (
            "uuid",
            "numero",
            "status",
            "criado_em",
            "alterado_em",
            "contrato",
            "empresa",
            "qtd_total_programada",
            "unidade_medida",
            "armazem",
            "etapas",
            "programacoes_de_recebimento",
            "ficha_tecnica",
            "custo_unitario_produto",
        )


class CronogramaComLogSerializer(serializers.ModelSerializer):
    etapas = EtapasDoCronogramaSerializer(many=True)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaSerializer(
        many=True
    )
    armazem = DistribuidorComEnderecoSimplesSerializer()
    status = serializers.CharField(source="get_status_display")
    empresa = TerceirizadaSimplesSerializer()
    contrato = ContratoSimplesSerializer()
    unidade_medida = UnidadeMedidaSerialzer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    ficha_tecnica = FichaTecnicaCronogramaSerializer()

    class Meta:
        model = Cronograma
        fields = (
            "uuid",
            "numero",
            "status",
            "criado_em",
            "alterado_em",
            "contrato",
            "empresa",
            "qtd_total_programada",
            "unidade_medida",
            "armazem",
            "etapas",
            "programacoes_de_recebimento",
            "ficha_tecnica",
            "custo_unitario_produto",
            "logs",
        )


class SolicitacaoAlteracaoCronogramaCompletoSerializer(serializers.ModelSerializer):
    fornecedor = serializers.CharField(source="cronograma.empresa")
    cronograma = CronogramaSerializer()
    status = serializers.CharField(source="get_status_display")
    etapas_antigas = EtapasDoCronogramaSerializer(many=True)
    etapas_novas = EtapasDoCronogramaSerializer(many=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = (
            "uuid",
            "numero_solicitacao",
            "fornecedor",
            "status",
            "criado_em",
            "cronograma",
            "etapas_antigas",
            "etapas_novas",
            "justificativa",
            "logs",
        )


class CronogramaRascunhosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cronograma
        fields = ("uuid", "numero", "alterado_em")


class CronogramaSimplesSerializer(serializers.ModelSerializer):
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()

    def get_pregao_chamada_publica(self, obj):
        return obj.contrato.pregao_chamada_publica if obj.contrato else None

    def get_nome_produto(self, obj):
        return obj.ficha_tecnica.produto.nome if obj.ficha_tecnica else None

    class Meta:
        model = Cronograma
        fields = ("uuid", "numero", "pregao_chamada_publica", "nome_produto")


class PainelCronogramaSerializer(serializers.ModelSerializer):
    produto = serializers.SerializerMethodField()
    empresa = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    def get_produto(self, obj):
        try:
            return obj.ficha_tecnica.produto.nome
        except AttributeError:
            return None

    def get_empresa(self, obj):
        return obj.empresa.razao_social if obj.empresa else None

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(
                    obj.log_mais_recente.criado_em, "%d/%m/%Y %H:%M"
                )
            return datetime.datetime.strftime(
                obj.log_mais_recente.criado_em, "%d/%m/%Y"
            )
        else:
            return datetime.datetime.strftime(obj.criado_em, "%d/%m/%Y")

    class Meta:
        model = Cronograma
        fields = ("uuid", "numero", "status", "empresa", "produto", "log_mais_recente")


class PainelSolicitacaoAlteracaoCronogramaSerializerItem(serializers.ModelSerializer):
    empresa = serializers.CharField(source="cronograma.empresa")
    cronograma = serializers.CharField(source="cronograma.numero")
    status = serializers.CharField(source="get_status_display")
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_criado_em:
            if obj.log_criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_criado_em, "%d/%m/%Y %H:%M")
            return datetime.datetime.strftime(obj.log_criado_em, "%d/%m/%Y")
        else:
            return datetime.datetime.strftime(obj.log_criado_em, "%d/%m/%Y")

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = (
            "uuid",
            "numero_solicitacao",
            "empresa",
            "status",
            "cronograma",
            "log_mais_recente",
        )


class PainelSolicitacaoAlteracaoCronogramaSerializer(serializers.Serializer):
    status = serializers.CharField()
    dados = serializers.SerializerMethodField()
    total = serializers.IntegerField(allow_null=True)

    def get_dados(self, obj):
        return PainelSolicitacaoAlteracaoCronogramaSerializerItem(
            obj["dados"], many=True
        ).data

    class Meta:
        model = SolicitacaoAlteracaoCronograma
        fields = ("uuid", "status", "total", "dados")

    def to_representation(self, instance):
        result = super(
            PainelSolicitacaoAlteracaoCronogramaSerializer, self
        ).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )


class LaboratorioSerializer(serializers.ModelSerializer):
    contatos = ContatoSimplesSerializer(many=True)

    class Meta:
        model = Laboratorio
        exclude = ("id",)


class LaboratorioSimplesFiltroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ("nome", "cnpj")
        read_only_fields = ("nome", "cnpj")


class LaboratorioCredenciadoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ("uuid", "nome")
        read_only_fields = ("uuid", "nome")


class UnidadeMedidaSerialzer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ("uuid", "nome", "abreviacao", "criado_em")
        read_only_fields = ("uuid", "nome", "abreviacao", "criado_em")


class ImagemDoTipoEmbalagemLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemDoTipoDeEmbalagem
        exclude = ("id", "uuid", "tipo_de_embalagem")


class TipoEmbalagemLayoutLookupSerializer(serializers.ModelSerializer):
    imagens = ImagemDoTipoEmbalagemLookupSerializer(many=True)

    class Meta:
        model = TipoDeEmbalagemDeLayout
        exclude = ("id", "layout_de_embalagem")


class LayoutDeEmbalagemSerializer(serializers.ModelSerializer):
    numero_ficha_tecnica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    def get_numero_ficha_tecnica(self, obj):
        return obj.ficha_tecnica.numero if obj.ficha_tecnica else None

    def get_nome_produto(self, obj):
        try:
            return obj.ficha_tecnica.produto.nome
        except AttributeError:
            None

    def get_pregao_chamada_publica(self, obj):
        return obj.ficha_tecnica.pregao_chamada_publica if obj.ficha_tecnica else None

    class Meta:
        model = LayoutDeEmbalagem
        fields = (
            "uuid",
            "numero_ficha_tecnica",
            "pregao_chamada_publica",
            "nome_produto",
            "status",
            "criado_em",
        )


class LayoutDeEmbalagemDetalheSerializer(serializers.ModelSerializer):
    numero_ficha_tecnica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    nome_empresa = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")
    tipos_de_embalagens = TipoEmbalagemLayoutLookupSerializer(many=True)
    log_mais_recente = serializers.SerializerMethodField()
    primeira_analise = serializers.SerializerMethodField()
    logs = LogSolicitacoesUsuarioSimplesSerializer(many=True)

    def get_numero_ficha_tecnica(self, obj):
        return obj.ficha_tecnica.numero if obj.ficha_tecnica else None

    def get_nome_produto(self, obj):
        try:
            return obj.ficha_tecnica.produto.nome
        except AttributeError:
            None

    def get_nome_empresa(self, obj):
        try:
            return obj.ficha_tecnica.empresa.razao_social
        except AttributeError:
            None

    def get_pregao_chamada_publica(self, obj):
        return obj.ficha_tecnica.pregao_chamada_publica if obj.ficha_tecnica else None

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            return datetime.datetime.strftime(
                obj.log_mais_recente.criado_em, "%d/%m/%Y - %H:%M"
            )
        else:
            return datetime.datetime.strftime(obj.criado_em, "%d/%m/%Y - %H:%M")

    def get_primeira_analise(self, obj):
        return obj.eh_primeira_analise

    class Meta:
        model = LayoutDeEmbalagem
        fields = (
            "uuid",
            "observacoes",
            "criado_em",
            "status",
            "tipos_de_embalagens",
            "numero_ficha_tecnica",
            "pregao_chamada_publica",
            "nome_produto",
            "nome_empresa",
            "log_mais_recente",
            "primeira_analise",
            "logs",
        )


class PainelLayoutEmbalagemSerializer(serializers.ModelSerializer):
    numero_ficha_tecnica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    nome_empresa = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")
    log_mais_recente = serializers.SerializerMethodField()

    def get_numero_ficha_tecnica(self, obj):
        try:
            return obj.ficha_tecnica.numero
        except AttributeError:
            return ""

    def get_nome_produto(self, obj):
        try:
            return obj.ficha_tecnica.produto.nome
        except AttributeError:
            return ""

    def get_nome_empresa(self, obj):
        try:
            return obj.ficha_tecnica.empresa.razao_social
        except AttributeError:
            return ""

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(
                    obj.log_mais_recente.criado_em, "%d/%m/%Y %H:%M"
                )
            return datetime.datetime.strftime(
                obj.log_mais_recente.criado_em, "%d/%m/%Y"
            )
        else:
            return datetime.datetime.strftime(obj.criado_em, "%d/%m/%Y")

    class Meta:
        model = LayoutDeEmbalagem
        fields = (
            "uuid",
            "numero_ficha_tecnica",
            "nome_produto",
            "nome_empresa",
            "status",
            "log_mais_recente",
        )


class DocumentoDeRecebimentoSerializer(serializers.ModelSerializer):
    criado_em = serializers.SerializerMethodField()
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return (
            obj.cronograma.contrato.numero_pregao if obj.cronograma.contrato else None
        )

    def get_nome_produto(self, obj):
        try:
            return obj.cronograma.ficha_tecnica.produto.nome
        except AttributeError:
            None

    def get_criado_em(self, obj):
        return obj.criado_em.strftime("%d/%m/%Y")

    class Meta:
        model = DocumentoDeRecebimento
        fields = (
            "uuid",
            "numero_cronograma",
            "numero_laudo",
            "pregao_chamada_publica",
            "nome_produto",
            "status",
            "criado_em",
        )


class PainelDocumentoDeRecebimentoSerializer(serializers.ModelSerializer):
    numero_cronograma = serializers.CharField(source="cronograma.numero")
    nome_produto = serializers.SerializerMethodField()
    nome_empresa = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")
    log_mais_recente = serializers.SerializerMethodField()

    def get_nome_produto(self, obj):
        try:
            return obj.cronograma.ficha_tecnica.produto.nome
        except AttributeError:
            return ""

    def get_nome_empresa(self, obj):
        try:
            return obj.cronograma.empresa.razao_social
        except AttributeError:
            return ""

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(
                    obj.log_mais_recente.criado_em, "%d/%m/%Y %H:%M"
                )
            return datetime.datetime.strftime(
                obj.log_mais_recente.criado_em, "%d/%m/%Y"
            )
        else:
            return datetime.datetime.strftime(obj.criado_em, "%d/%m/%Y")

    class Meta:
        model = DocumentoDeRecebimento
        fields = (
            "uuid",
            "numero_cronograma",
            "nome_produto",
            "nome_empresa",
            "status",
            "log_mais_recente",
        )


class ArquivoDoTipoDeDocumentoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArquivoDoTipoDeDocumento
        exclude = ("id", "uuid", "tipo_de_documento")


class TipoDocumentoDeRecebimentoLookupSerializer(serializers.ModelSerializer):
    arquivos = ArquivoDoTipoDeDocumentoLookupSerializer(many=True)

    class Meta:
        model = TipoDeDocumentoDeRecebimento
        exclude = ("id", "documento_recebimento")


class DocRecebimentoDetalharSerializer(serializers.ModelSerializer):
    criado_em = serializers.SerializerMethodField()
    numero_cronograma = serializers.SerializerMethodField()
    pregao_chamada_publica = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")
    tipos_de_documentos = TipoDocumentoDeRecebimentoLookupSerializer(many=True)
    logs = LogSolicitacoesUsuarioSimplesSerializer(many=True)

    def get_numero_cronograma(self, obj):
        return obj.cronograma.numero if obj.cronograma else None

    def get_pregao_chamada_publica(self, obj):
        return (
            obj.cronograma.contrato.numero_pregao if obj.cronograma.contrato else None
        )

    def get_nome_produto(self, obj):
        try:
            return obj.cronograma.ficha_tecnica.produto.nome
        except AttributeError:
            return None

    def get_criado_em(self, obj):
        return obj.criado_em.strftime("%d/%m/%Y")

    class Meta:
        model = DocumentoDeRecebimento
        fields = (
            "uuid",
            "numero_cronograma",
            "pregao_chamada_publica",
            "nome_produto",
            "numero_laudo",
            "status",
            "criado_em",
            "tipos_de_documentos",
            "correcao_solicitada",
            "logs",
        )


class DataDeFabricacaoEPrazoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeFabricaoEPrazo
        exclude = ("id", "documento_recebimento")


class DocRecebimentoDetalharCodaeSerializer(DocRecebimentoDetalharSerializer):
    laboratorio = LaboratorioCredenciadoSimplesSerializer()
    unidade_medida = NomeEAbreviacaoUnidadeMedidaSerializer()
    datas_fabricacao_e_prazos = DataDeFabricacaoEPrazoLookupSerializer(many=True)
    numero_sei = serializers.SerializerMethodField()
    fornecedor = serializers.SerializerMethodField()

    def get_numero_sei(self, obj):
        return obj.cronograma.contrato.processo if obj.cronograma.contrato else None

    def get_fornecedor(self, obj):
        return obj.cronograma.empresa.nome_fantasia if obj.cronograma.empresa else None

    class Meta(DocRecebimentoDetalharSerializer.Meta):
        fields = DocRecebimentoDetalharSerializer.Meta.fields + (
            "fornecedor",
            "numero_sei",
            "laboratorio",
            "quantidade_laudo",
            "unidade_medida",
            "saldo_laudo",
            "data_fabricacao_lote",
            "validade_produto",
            "data_final_lote",
            "datas_fabricacao_e_prazos",
            "correcao_solicitada",
        )


class FichaTecnicaListagemSerializer(serializers.ModelSerializer):
    nome_produto = serializers.SerializerMethodField()
    criado_em = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    def get_nome_produto(self, obj):
        return obj.produto.nome if obj.produto else None

    def get_criado_em(self, obj):
        return obj.criado_em.strftime("%d/%m/%Y")

    class Meta:
        model = FichaTecnicaDoProduto
        fields = (
            "uuid",
            "numero",
            "nome_produto",
            "pregao_chamada_publica",
            "criado_em",
            "status",
        )


class InformacoesNutricionaisFichaTecnicaSerializer(serializers.ModelSerializer):
    informacao_nutricional = InformacaoNutricionalSerializer()

    class Meta:
        model = InformacoesNutricionaisFichaTecnica
        fields = (
            "uuid",
            "informacao_nutricional",
            "quantidade_por_100g",
            "quantidade_porcao",
            "valor_diario",
        )
        read_only_fields = ("uuid",)


class FichaTecnicaDetalharSerializer(serializers.ModelSerializer):
    criado_em = serializers.SerializerMethodField()
    produto = NomeDeProdutoEditalSerializer()
    marca = MarcaSimplesSerializer()
    empresa = TerceirizadaLookUpSerializer()
    fabricante = FabricanteSimplesSerializer()
    unidade_medida_porcao = NomeEAbreviacaoUnidadeMedidaSerializer()
    status = serializers.CharField(source="get_status_display", read_only=True)
    informacoes_nutricionais = InformacoesNutricionaisFichaTecnicaSerializer(many=True)
    unidade_medida_primaria = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_secundaria = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_primaria_vazia = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_secundaria_vazia = NomeEAbreviacaoUnidadeMedidaSerializer()
    unidade_medida_volume_primaria = NomeEAbreviacaoUnidadeMedidaSerializer()

    def get_criado_em(self, obj):
        return obj.criado_em.strftime("%d/%m/%Y")

    class Meta:
        model = FichaTecnicaDoProduto
        fields = (
            "uuid",
            "numero",
            "produto",
            "pregao_chamada_publica",
            "marca",
            "categoria",
            "status",
            "criado_em",
            "empresa",
            "fabricante",
            "cnpj_fabricante",
            "cep_fabricante",
            "endereco_fabricante",
            "numero_fabricante",
            "complemento_fabricante",
            "bairro_fabricante",
            "cidade_fabricante",
            "estado_fabricante",
            "email_fabricante",
            "telefone_fabricante",
            "prazo_validade",
            "numero_registro",
            "agroecologico",
            "organico",
            "mecanismo_controle",
            "componentes_produto",
            "alergenicos",
            "ingredientes_alergenicos",
            "gluten",
            "lactose",
            "lactose_detalhe",
            "porcao",
            "unidade_medida_porcao",
            "valor_unidade_caseira",
            "unidade_medida_caseira",
            "informacoes_nutricionais",
            "prazo_validade_descongelamento",
            "condicoes_de_conservacao",
            "temperatura_congelamento",
            "temperatura_veiculo",
            "condicoes_de_transporte",
            "embalagem_primaria",
            "embalagem_secundaria",
            "embalagens_de_acordo_com_anexo",
            "material_embalagem_primaria",
            "produto_eh_liquido",
            "volume_embalagem_primaria",
            "unidade_medida_volume_primaria",
            "peso_liquido_embalagem_primaria",
            "unidade_medida_primaria",
            "peso_liquido_embalagem_secundaria",
            "unidade_medida_secundaria",
            "peso_embalagem_primaria_vazia",
            "unidade_medida_primaria_vazia",
            "peso_embalagem_secundaria_vazia",
            "unidade_medida_secundaria_vazia",
            "variacao_percentual",
            "sistema_vedacao_embalagem_secundaria",
            "rotulo_legivel",
            "nome_responsavel_tecnico",
            "habilitacao",
            "numero_registro_orgao",
            "arquivo",
            "modo_de_preparo",
            "informacoes_adicionais",
        )


class AnaliseFichaTecnicaSerializer(serializers.ModelSerializer):
    aprovada = serializers.BooleanField()

    class Meta:
        model = AnaliseFichaTecnica
        exclude = ("id", "ficha_tecnica")


class FichaTecnicaComAnaliseDetalharSerializer(FichaTecnicaDetalharSerializer):
    analise = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()

    def get_analise(self, obj):
        analise_mais_recente = obj.analises.order_by("-criado_em").first()

        return (
            AnaliseFichaTecnicaSerializer(analise_mais_recente).data
            if analise_mais_recente
            else None
        )

    def get_log_mais_recente(self, obj):
        log_mais_recente = obj.log_mais_recente

        if log_mais_recente:
            return datetime.datetime.strftime(
                log_mais_recente.criado_em, "%d/%m/%Y - %H:%M"
            )

        else:
            return datetime.datetime.strftime(obj.alterado_em, "%d/%m/%Y - %H:%M")

    class Meta(FichaTecnicaDetalharSerializer.Meta):
        fields = FichaTecnicaDetalharSerializer.Meta.fields + (
            "analise",
            "log_mais_recente",
        )


class PainelFichaTecnicaSerializer(serializers.ModelSerializer):
    numero_ficha = serializers.CharField(source="numero")
    nome_produto = serializers.CharField(source="produto.nome")
    nome_empresa = serializers.CharField(source="empresa.nome_fantasia")
    status = serializers.CharField(source="get_status_display")
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(
                    obj.log_mais_recente.criado_em, "%d/%m/%Y %H:%M"
                )
            return datetime.datetime.strftime(
                obj.log_mais_recente.criado_em, "%d/%m/%Y"
            )
        else:
            return datetime.datetime.strftime(obj.criado_em, "%d/%m/%Y")

    class Meta:
        model = FichaTecnicaDoProduto
        fields = (
            "uuid",
            "numero_ficha",
            "nome_produto",
            "nome_empresa",
            "status",
            "log_mais_recente",
        )
