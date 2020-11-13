from rest_framework import serializers

from sme_terceirizadas.logistica.models import Alimento, Guia, SolicitacaoRemessa


class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        exclude = ('id',)


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


class SolicitacaoRemessaSerializer(serializers.ModelSerializer):
    guias = serializers.SerializerMethodField()

    def get_guias(self, obj):
        return GuiaSerializer(
            Guia.objects.filter(
                solicitacao=obj.id
            ),
            many=True
        ).data

    class Meta:
        model = SolicitacaoRemessa
        exclude = ('id',)


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
