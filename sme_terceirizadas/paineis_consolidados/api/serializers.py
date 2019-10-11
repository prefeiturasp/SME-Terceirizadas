import datetime

from django.utils import timezone
from rest_framework import serializers

from ..models import SolicitacoesCODAE


class SolicitacoesSerializer(serializers.ModelSerializer):
    data_log = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()
    prioridade = serializers.CharField()

    def get_descricao(self, obj):
        uuid = str(obj.uuid)
        return f'{uuid.upper()[:5]} - {obj.lote[:20]} - {obj.desc_doc}'

    def get_data_log(self, obj):
        criado_em = obj.criado_em.astimezone(timezone.get_current_timezone())
        if criado_em.date() == datetime.date.today():
            return criado_em.strftime('%H:%M')
        return criado_em.strftime('%d/%m/%Y')

    class Meta:
        fields = '__all__'
        model = SolicitacoesCODAE
