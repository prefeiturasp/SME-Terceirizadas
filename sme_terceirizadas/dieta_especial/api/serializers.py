from rest_framework import serializers

from ..models import SolicitacaoDietaEspecial


class SolicitacaoDietaEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'codigo_eol_aluno',
            'nome_completo_aluno',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'data_nascimento_aluno',
            'observacoes'
        )
