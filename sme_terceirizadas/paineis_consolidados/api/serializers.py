import datetime

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


class SolicitacoesExportXLSXSerializer(serializers.ModelSerializer):
    lote_nome = serializers.CharField()
    escola_nome = serializers.CharField()
    desc_doc = serializers.CharField()
    data_evento = serializers.SerializerMethodField()
    numero_alunos = serializers.SerializerMethodField()
    observacoes = serializers.SerializerMethodField()
    data_autorizacao = serializers.SerializerMethodField()

    def get_numero_alunos(self, obj):
        return obj.get_raw_model.objects.get(uuid=obj.uuid).numero_alunos

    def get_data_evento(self, obj):
        if obj.data_evento_fim and obj.data_evento and obj.data_evento != obj.data_evento_fim:
            return f"{obj.data_evento.strftime('%d/%m/%Y')} - {obj.data_evento_fim.strftime('%d/%m/%Y')}"
        elif obj.tipo_doc in ['INC_ALIMENTA', 'SUSP_ALIMENTACAO', 'INC_ALIMENTA_CEMEI']:
            return obj.get_raw_model.objects.get(uuid=obj.uuid).datas
        return obj.data_evento.strftime('%d/%m/%Y') if obj.data_evento else None

    def get_data_autorizacao(self, obj):
        return obj.get_raw_model.objects.get(uuid=obj.uuid).data_autorizacao

    def get_observacoes(self, obj):
        model_obj = obj.get_raw_model.objects.get(uuid=obj.uuid)
        if hasattr(model_obj, 'observacao'):
            return model_obj.observacao.replace('<p>', '').replace('</p>', '') if model_obj.observacao else None
        elif hasattr(model_obj, 'observacoes'):
            return model_obj.observacoes.replace('<p>', '').replace('</p>', '') if model_obj.observacoes else None
        return None

    class Meta:
        model = SolicitacoesCODAE
        fields = (
            'lote_nome',
            'escola_nome',
            'desc_doc',
            'data_evento',
            'numero_alunos',
            'observacoes',
            'data_autorizacao'
        )

    def __init__(self, *args, **kwargs):
        """Não retornar campo data_ultimo_log caso status da solicitação for 'AUTORIZADAS'."""
        if kwargs['context']['status'] == 'AUTORIZADAS':
            del self.fields['data_ultimo_log']

        super().__init__(*args, **kwargs)
