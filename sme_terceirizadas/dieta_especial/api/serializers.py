from rest_framework import serializers

from ...dados_comuns.validators import deve_ser_no_passado
from ..models import SolicitacaoDietaEspecial


class SolicitacaoDietaEspecialSerializer(serializers.ModelSerializer):

    def validate_data_nascimento_aluno(self, data_nascimento_aluno):
        deve_ser_no_passado(data_nascimento_aluno)
        return data_nascimento_aluno

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        solicitacao = SolicitacaoDietaEspecial.objects.create(**validated_data)
        return solicitacao

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'codigo_eol_aluno',
            'nome_completo_aluno',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'data_nascimento_aluno',
            'observacoes',
            'criado_em'
        )
