import datetime

from rest_framework import serializers

from ..models import SolicitacoesAutorizadasDRE, SolicitacoesPendentesDRE


class SolicitacoesDRESerializer(serializers.ModelSerializer):
    # TODO Campos para compatibilidade com o Front atual. Rever o front e remover os campos calculados.
    date = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    def get_text(self, obj):
        uuid = str(obj.uuid)
        return f'{uuid.upper()[:5]} - {obj.lote[:20]} - {obj.tipo_doc}'

    def get_date(self, obj):
        if obj.data.date() == datetime.date.today():
            return f'{obj.data.time():%H:%M}'
        return f'{obj.data.date():%d/%m/%Y}'

    class Meta:
        abstract = True


class SolicitacoesAutorizadasDRESerializer(SolicitacoesDRESerializer):

    class Meta:
        fields = '__all__'
        model = SolicitacoesAutorizadasDRE


class SolicitacoesPendentesDRESerializer(SolicitacoesDRESerializer):

    class Meta:
        fields = '__all__'
        model = SolicitacoesPendentesDRE





