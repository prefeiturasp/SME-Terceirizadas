import datetime

from django.utils import timezone
from rest_framework import serializers

from ..models import SolicitacoesCODAE


class SolicitacoesSerializer(serializers.ModelSerializer):
    data_log = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()
    descricao_dieta_especial = serializers.SerializerMethodField()
    prioridade = serializers.CharField()
    id_externo = serializers.CharField()

    def get_descricao_dieta_especial(self, obj):
        return f'{obj.codigo_eol_aluno if obj.codigo_eol_aluno else "(Aluno não matriculado)"} - {obj.nome_aluno}'

    def get_descricao(self, obj):
        uuid = str(obj.uuid)
        descricao = f'{uuid.upper()[:5]} - {obj.lote_nome[:20]} - {obj.desc_doc}'
        if obj.tipo_solicitacao_dieta == 'ALUNO_NAO_MATRICULADO':
            descricao = f'{descricao} - Não matriculados'
        if obj.tipo_solicitacao_dieta == 'ALTERACAO_UE':
            descricao = f'{descricao} - Alteração U.E'
        return descricao

    def get_data_log(self, obj):
        if obj.data_log.date() == datetime.date.today():
            return obj.data_log.strftime('%d/%m/%Y %H:%M')
        return obj.data_log.strftime('%d/%m/%Y')

    class Meta:
        fields = '__all__'
        model = SolicitacoesCODAE
