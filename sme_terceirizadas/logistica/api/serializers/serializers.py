from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesSerializer
from sme_terceirizadas.logistica.models import (
    Alimento,
    Guia,
    SolicitacaoDeAlteracaoRequisicao,
    SolicitacaoRemessa,
    TipoEmbalagem
)


class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        exclude = ('id',)


class AlimentoLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = ('uuid', 'nome_alimento', 'qtd_volume', 'embalagem')


class GuiaSerializer(serializers.ModelSerializer):
    alimentos = serializers.SerializerMethodField()

    def get_alimentos(self, obj):
        return AlimentoSerializer(
            Alimento.objects.filter(
                guia=obj.id
            ),
            many=True
        ).data

    class Meta:
        model = Guia
        exclude = ('id',)


class GuiaLookUpSerializer(serializers.ModelSerializer):
    alimentos = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_alimentos(self, obj):
        return AlimentoLookUpSerializer(
            Alimento.objects.filter(
                guia=obj.id
            ),
            many=True
        ).data

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
    guias = serializers.SerializerMethodField()
    distribuidor_nome = serializers.SerializerMethodField()

    def get_guias(self, obj):
        return GuiaLookUpSerializer(
            Guia.objects.filter(
                solicitacao=obj.id
            ),
            many=True
        ).data

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
    id_externo = serializers.SerializerMethodField()

    def get_id_externo(self, obj):
        return obj.id_externo

    class Meta:
        model = SolicitacaoDeAlteracaoRequisicao
        exclude = ('id',)
