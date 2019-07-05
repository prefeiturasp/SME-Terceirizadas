from datetime import date

from rest_framework import serializers
from traitlets import Any

from sme_pratoaberto_terceirizadas.dados_comuns.validators import nao_pode_ser_passado, nao_pode_ser_feriado, \
    objeto_nao_deve_ter_duplicidade
from ..models import *


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        fields = ['uuid', 'nome']


class CardapioSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)

    def validate_data(self, data: date) -> Any:
        nao_pode_ser_passado(data)
        nao_pode_ser_feriado(data)
        objeto_nao_deve_ter_duplicidade(
            Cardapio,
            mensagem='Já existe um cardápio cadastrado com esta data',
            data=data
        )
        return data

    class Meta:
        model = Cardapio
        fields = ['uuid', 'data', 'ativo', 'criado_em', 'tipos_alimentacao']
