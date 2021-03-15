from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesSerializer
from sme_terceirizadas.logistica.models import (
    Alimento,
    Embalagem,
    Guia,
    SolicitacaoDeAlteracaoRequisicao,
    SolicitacaoRemessa,
    TipoEmbalagem
)


class EmbalagemSerializer(serializers.ModelSerializer):
    tipo_embalagem = serializers.SerializerMethodField()

    def get_tipo_embalagem(self, obj):
        return obj.get_tipo_embalagem_display()

    class Meta:
        model = Embalagem
        exclude = ('id',)


class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        exclude = ('id',)


class AlimentoLookUpSerializer(serializers.ModelSerializer):
    embalagens = EmbalagemSerializer(many=True)

    class Meta:
        model = Alimento
        fields = ('uuid', 'nome_alimento', 'embalagens')


class GuiaSerializer(serializers.ModelSerializer):
    alimentos = AlimentoSerializer(many=True)

    class Meta:
        model = Guia
        exclude = ('id',)


class GuiaLookUpSerializer(serializers.ModelSerializer):
    alimentos = AlimentoLookUpSerializer(many=True)
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Guia
        fields = ('uuid', 'numero_guia', 'data_entrega', 'codigo_unidade', 'nome_unidade', 'endereco_unidade',
                  'numero_unidade', 'bairro_unidade', 'bairro_unidade', 'cep_unidade', 'cidade_unidade',
                  'estado_unidade', 'contato_unidade', 'telefone_unidade', 'alimentos', 'status')


class SolicitacaoRemessaSerializer(serializers.ModelSerializer):

    logs = LogSolicitacoesSerializer(many=True)
    guias = GuiaSerializer(many=True)

    class Meta:
        model = SolicitacaoRemessa
        exclude = ('id',)


class SolicitacaoRemessaLookUpSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    guias = GuiaLookUpSerializer(many=True)
    distribuidor_nome = serializers.SerializerMethodField()

    def get_distribuidor_nome(self, obj):
        return obj.distribuidor.razao_social

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = SolicitacaoRemessa
        fields = ('uuid', 'numero_solicitacao', 'distribuidor_nome', 'status', 'guias')


class XmlAlimentoSerializer(serializers.Serializer):
    StrCodSup = serializers.CharField()
    StrCodPapa = serializers.CharField()
    StrNomAli = serializers.CharField()
    StrEmbala = serializers.CharField()
    IntQtdVol = serializers.CharField()


class XmlGuiaSerializer(serializers.Serializer):
    StrNumGui = serializers.CharField()
    DtEntrega = serializers.DateField()
    StrCodUni = serializers.CharField()
    StrNomUni = serializers.CharField()
    StrEndUni = serializers.CharField()
    StrNumUni = serializers.CharField()
    StrBaiUni = serializers.CharField()
    StrCepUni = serializers.CharField()
    StrCidUni = serializers.CharField()
    StrEstUni = serializers.CharField()
    StrConUni = serializers.CharField()
    StrTelUni = serializers.CharField()
    alimentos = XmlAlimentoSerializer(many=True)


class XmlParserSolicitacaoSerializer(serializers.Serializer):
    StrCnpj = serializers.CharField(max_length=14)
    StrNumSol = serializers.CharField(max_length=30)
    guias = XmlGuiaSerializer(many=True)


class TipoEmbalagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEmbalagem
        exclude = ('id',)


class SolicitacaoRemessaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRemessa
        fields = ('uuid', 'numero_solicitacao')


class GuiaDaRemessaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        exclude = ('id',)


class GuiaDaRemessaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        fields = ('uuid', 'numero_guia')


class InfoUnidadesSimplesDaGuiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        fields = ('codigo_unidade', 'nome_unidade')


class AlimentoDaGuiaDaRemessaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        exclude = ('id',)


class AlimentoDaGuiaDaRemessaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = ('uuid', 'nome_alimento')


class SolicitacaoDeAlteracaoSerializer(serializers.ModelSerializer):
    motivo = serializers.CharField(source='get_motivo_display')
    requisicao = SolicitacaoRemessaSimplesSerializer(read_only=True, many=False)
    nome_distribuidor = serializers.CharField()
    qtd_guias = serializers.IntegerField()
    status = serializers.SerializerMethodField()
    criado_em = serializers.SerializerMethodField()
    data_entrega = serializers.SerializerMethodField()

    def get_criado_em(self, obj):
        return obj.criado_em.strftime('%d/%m/%Y')

    def get_data_entrega(self, obj):
        return obj.data_entrega.strftime('%d/%m/%Y')

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = SolicitacaoDeAlteracaoRequisicao
        exclude = ('id',)


class SolicitacaoDeAlteracaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoDeAlteracaoRequisicao
        fields = ('uuid', 'numero_solicitacao')
