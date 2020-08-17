import datetime

from rest_framework import serializers

from ....dados_comuns.api.serializers import (
    LogSolicitacoesUsuarioComAnexosSerializer,
    LogSolicitacoesUsuarioComVinculoSerializer,
    LogSolicitacoesUsuarioSerializer
)
from ....dados_comuns.fluxo_status import ReclamacaoProdutoWorkflow
from ....escola.api.serializers import EscolaSimplissimaSerializer
from ....terceirizada.api.serializers.serializers import TerceirizadaSimplesSerializer
from ...models import (
    AnexoReclamacaoDeProduto,
    Fabricante,
    HomologacaoDoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    LogSolicitacoesUsuario,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
    ReclamacaoDeProduto,
    RespostaAnaliseSensorial,
    TipoDeInformacaoNutricional
)


class FabricanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        exclude = ('id',)


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        exclude = ('id',)


class ProtocoloDeDietaEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloDeDietaEspecial
        exclude = ('id', 'ativo', 'criado_em', 'criado_por',)


class AnexoReclamacaoDeProdutoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        request = self.context.get('request')
        arquivo = obj.arquivo.url
        return request.build_absolute_uri(arquivo)

    class Meta:
        model = AnexoReclamacaoDeProduto
        fields = ('arquivo', 'nome', 'uuid')


class ImagemDoProdutoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        request = self.context.get('request')
        arquivo = obj.arquivo.url
        return request.build_absolute_uri(arquivo)

    class Meta:
        model = ImagemDoProduto
        fields = ('arquivo', 'nome', 'uuid')


class TipoDeInformacaoNutricionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDeInformacaoNutricional
        exclude = ('id',)


class InformacaoNutricionalSerializer(serializers.ModelSerializer):
    tipo_nutricional = TipoDeInformacaoNutricionalSerializer()

    class Meta:
        model = InformacaoNutricional
        exclude = ('id',)


class InformacoesNutricionaisDoProdutoSerializer(serializers.ModelSerializer):
    informacao_nutricional = InformacaoNutricionalSerializer()

    class Meta:
        model = InformacoesNutricionaisDoProduto
        exclude = ('id', 'produto')


class ReclamacaoDeProdutoSerializer(serializers.ModelSerializer):
    escola = EscolaSimplissimaSerializer()
    anexos = serializers.SerializerMethodField()
    status_titulo = serializers.CharField(source='status.state.title')
    logs = serializers.SerializerMethodField()

    def get_anexos(self, obj):
        return AnexoReclamacaoDeProdutoSerializer(
            obj.anexos.all(),
            context=self.context,
            many=True
        ).data

    def get_logs(self, obj):
        return LogSolicitacoesUsuarioSerializer(
            LogSolicitacoesUsuario.objects.filter(uuid_original=obj.uuid).order_by('criado_em'),
            many=True
        ).data

    class Meta:
        model = ReclamacaoDeProduto
        fields = ('uuid', 'reclamante_registro_funcional', 'logs', 'reclamante_cargo', 'reclamante_nome',
                  'reclamacao', 'escola', 'anexos', 'status', 'status_titulo', 'criado_em', 'id_externo')


class ReclamacaoDeProdutoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReclamacaoDeProduto
        fields = ('reclamacao', 'criado_em')


class HomologacaoProdutoSimplesSerializer(serializers.ModelSerializer):
    reclamacoes = serializers.SerializerMethodField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    logs = LogSolicitacoesUsuarioComVinculoSerializer(many=True)

    def get_reclamacoes(self, obj):
        return ReclamacaoDeProdutoSerializer(
            obj.reclamacoes.all(), context=self.context,
            many=True
        ).data

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'status', 'id_externo', 'rastro_terceirizada', 'logs',
                  'criado_em', 'reclamacoes')


class HomologacaoProdutoComUltimoLogSerializer(serializers.ModelSerializer):
    reclamacoes = serializers.SerializerMethodField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    logs = LogSolicitacoesUsuarioComVinculoSerializer(many=True)
    ultimo_log = LogSolicitacoesUsuarioComVinculoSerializer()
    status_titulo = serializers.CharField(source='status.state.title')

    def get_reclamacoes(self, obj):
        return ReclamacaoDeProdutoSerializer(
            obj.reclamacoes.all(), context=self.context,
            many=True
        ).data

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'status', 'id_externo', 'rastro_terceirizada', 'logs',
                  'criado_em', 'reclamacoes', 'ultimo_log', 'tempo_aguardando_acao_em_dias',
                  'status_titulo')


class ProdutoSerializer(serializers.ModelSerializer):
    protocolos = ProtocoloDeDietaEspecialSerializer(many=True)
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    imagens = serializers.ListField(
        child=ImagemDoProdutoSerializer(), required=True
    )
    id_externo = serializers.CharField()

    informacoes_nutricionais = serializers.SerializerMethodField()

    homologacoes = serializers.SerializerMethodField()

    ultima_homologacao = HomologacaoProdutoComUltimoLogSerializer()

    def get_homologacoes(self, obj):
        return HomologacaoProdutoComUltimoLogSerializer(
            HomologacaoDoProduto.objects.filter(
                produto=obj
            ), context=self.context,
            many=True
        ).data

    def get_informacoes_nutricionais(self, obj):
        return InformacoesNutricionaisDoProdutoSerializer(
            InformacoesNutricionaisDoProduto.objects.filter(
                produto=obj
            ), many=True
        ).data

    class Meta:
        model = Produto
        exclude = ('id',)


class ProdutoSemAnexoSerializer(serializers.ModelSerializer):
    protocolos = ProtocoloDeDietaEspecialSerializer(many=True)
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    id_externo = serializers.CharField()

    informacoes_nutricionais = serializers.SerializerMethodField()

    homologacoes = serializers.SerializerMethodField()

    ultima_homologacao = HomologacaoProdutoSimplesSerializer()

    def get_homologacoes(self, obj):
        return HomologacaoProdutoSimplesSerializer(
            HomologacaoDoProduto.objects.filter(
                produto=obj
            ), context=self.context,
            many=True
        ).data

    def get_informacoes_nutricionais(self, obj):
        return InformacoesNutricionaisDoProdutoSerializer(
            InformacoesNutricionaisDoProduto.objects.filter(
                produto=obj
            ), many=True
        ).data

    class Meta:
        model = Produto
        exclude = ('id',)


class ProdutoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ('uuid', 'nome',)


class MarcaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ('uuid', 'nome',)


class FabricanteSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        fields = ('uuid', 'nome',)


class ProtocoloSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloDeDietaEspecial
        fields = ('uuid', 'nome',)


class HomologacaoProdutoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'produto', 'status', 'id_externo', 'logs', 'rastro_terceirizada', 'pdf_gerado',
                  'protocolo_analise_sensorial')


class HomologacaoProdutoBase(serializers.ModelSerializer):
    qtde_reclamacoes = serializers.SerializerMethodField()
    qtde_questionamentos = serializers.SerializerMethodField()

    def get_qtde_reclamacoes(self, obj):
        return ReclamacaoDeProduto.objects.filter(homologacao_de_produto=obj).count()

    def get_qtde_questionamentos(self, obj):
        return ReclamacaoDeProduto.objects.filter(
            homologacao_de_produto=obj,
            status=ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA).count()


class HomologacaoProdutoPainelGerencialSerializer(HomologacaoProdutoBase):
    nome_produto = serializers.SerializerMethodField()
    log_mais_recente = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        if obj.log_mais_recente:
            if obj.log_mais_recente.criado_em.date() == datetime.date.today():
                return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M')
            return datetime.datetime.strftime(obj.log_mais_recente.criado_em, '%d/%m/%Y')
        else:
            return datetime.datetime.strftime(obj.criado_em, '%d/%m/%Y')

    def get_nome_produto(self, obj):
        return obj.produto.nome

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'nome_produto', 'status', 'id_externo', 'log_mais_recente',
                  'qtde_reclamacoes', 'qtde_questionamentos')


class HomologacaoProdutoComLogsDetalhadosSerializer(serializers.ModelSerializer):
    produto = ProdutoSemAnexoSerializer()
    logs = LogSolicitacoesUsuarioComAnexosSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'produto', 'status', 'id_externo', 'logs', 'rastro_terceirizada', 'pdf_gerado',
                  'protocolo_analise_sensorial')


class HomologacaoProdutoResponderReclamacaoTerceirizadaSerializer(HomologacaoProdutoBase):
    reclamacoes = serializers.SerializerMethodField()

    def get_reclamacoes(self, obj):
        return ReclamacaoDeProdutoSerializer(
            obj.reclamacoes.filter(
                status__in=[ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA,
                            ReclamacaoProdutoWorkflow.RESPONDIDO_TERCEIRIZADA]), context=self.context,
            many=True
        ).data

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'status', 'id_externo', 'criado_em', 'reclamacoes',
                  'qtde_reclamacoes', 'qtde_questionamentos')


class ProdutoResponderReclamacaoTerceirizadaSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    id_externo = serializers.CharField()
    ultima_homologacao = HomologacaoProdutoResponderReclamacaoTerceirizadaSerializer()

    class Meta:
        model = Produto
        exclude = ('id',)


class RespostaAnaliseSensorialSerializer(serializers.ModelSerializer):

    class Meta:
        model = RespostaAnaliseSensorial
        fields = ('uuid', 'responsavel_produto', 'registro_funcional', 'id_externo', 'data', 'hora',
                  'observacao', 'criado_em')


class HomologacaoRelatorioAnaliseSensorialSerializer(serializers.ModelSerializer):
    log_resposta_analise = serializers.SerializerMethodField()
    log_solicitacao_analise = serializers.SerializerMethodField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    resposta_analise = serializers.SerializerMethodField()

    def get_resposta_analise(self, obj):
        return RespostaAnaliseSensorialSerializer(
            RespostaAnaliseSensorial.objects.filter(homologacao_de_produto=obj).order_by('criado_em').last()).data

    def get_log_resposta_analise(self, obj):
        return LogSolicitacoesUsuarioSerializer(
            LogSolicitacoesUsuario.objects.filter(
                uuid_original=obj.uuid,
                status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_ANALISE_SENSORIAL
            ).order_by('criado_em').last()).data

    def get_log_solicitacao_analise(self, obj):
        return LogSolicitacoesUsuarioSerializer(
            LogSolicitacoesUsuario.objects.filter(
                uuid_original=obj.uuid,
                status_evento=LogSolicitacoesUsuario.CODAE_PEDIU_ANALISE_SENSORIAL,
                criado_em__lte=obj.respostas_analise.last().criado_em
            ).order_by('criado_em').last()).data

    class Meta:
        model = HomologacaoDoProduto
        fields = ('uuid', 'status', 'id_externo', 'log_resposta_analise', 'log_solicitacao_analise',
                  'rastro_terceirizada', 'protocolo_analise_sensorial', 'resposta_analise')


class ProdutoRelatorioAnaliseSensorialSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    id_externo = serializers.CharField()
    ultima_homologacao = HomologacaoRelatorioAnaliseSensorialSerializer()

    class Meta:
        model = Produto
        exclude = ('id',)


class UltimoLogRelatorioSituacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('criado_em')


class HomologacaoRelatorioSituacaoSerializer(serializers.ModelSerializer):
    ultimo_log = UltimoLogRelatorioSituacaoSerializer()
    status_titulo = serializers.CharField(source='status.state.title')

    class Meta:
        model = HomologacaoDoProduto
        fields = ('tempo_aguardando_acao_em_dias', 'ultimo_log', 'status_titulo')


class ProdutoRelatorioSituacaoSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer()
    fabricante = FabricanteSerializer()
    ultima_homologacao = HomologacaoRelatorioSituacaoSerializer()

    class Meta:
        model = Produto
        include = ('nome', 'marca', 'fabricante', 'criado_em', 'ultima_homologacao',
                   'eh_para_alunos_com_dieta', 'tem_aditivos_alergenicos')
