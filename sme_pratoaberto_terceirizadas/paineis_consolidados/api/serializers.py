import datetime

from rest_framework import serializers

from ..models import SolicitacoesAutorizadasDRE, SolicitacoesPendentesDRE
from ..models.codae import SolicitacoesCODAE


class SolicitacoesDRESerializer(serializers.ModelSerializer):
    # TODO Campos para compatibilidade com o Front atual. Rever o front e remover os campos calculados.
    date = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    def get_text(self, obj):
        uuid = str(obj.uuid)
        return f'{uuid.upper()[:5]} - {obj.lote[:20]} - {obj.tipo_doc}'

    def get_date(self, obj):
        if obj.data_log.date() == datetime.date.today():
            return f'{obj.data_log.time():%H:%M}'
        return f'{obj.data_log.date():%d/%m/%Y}'

    class Meta:
        abstract = True


class SolicitacoesAutorizadasDRESerializer(SolicitacoesDRESerializer):
    class Meta:
        fields = '__all__'
        model = SolicitacoesAutorizadasDRE


class SolicitacoesPendentesDRESerializer(SolicitacoesDRESerializer):
    prioridade = serializers.SerializerMethodField()

    def get_prioridade(self, obj):
        return obj.prioridade

    class Meta:
        fields = '__all__'
        model = SolicitacoesPendentesDRE


class SolicitacoesSerializer(serializers.ModelSerializer):
    data_log = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()

    def get_descricao(self, obj):
        uuid = str(obj.uuid)
        return f'{uuid.upper()[:5]} - {obj.lote[:20]} - {obj.tipo_doc}'

    def get_data_log(self, obj):
        criado_em = obj.criado_em
        if criado_em.date() == datetime.date.today():
            return criado_em.strftime('%H:%M')
        return criado_em.strftime('%d/%m/%Y')

    class Meta:
        fields = '__all__'
        model = SolicitacoesCODAE
