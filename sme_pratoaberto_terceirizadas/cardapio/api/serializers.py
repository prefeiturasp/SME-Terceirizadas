from datetime import date

from rest_framework import serializers
from traitlets import Any

from sme_pratoaberto_terceirizadas.dados_comuns.validators import (nao_pode_ser_passado, nao_pode_ser_feriado, \
                                                                   objeto_nao_deve_ter_duplicidade, verificar_se_existe)
from ..models import *
from .validators import cardapio_antigo, cardapio_existe, valida_cardapio_de_para


class TipoAlimentacaoSerializer(serializers.ModelSerializer):

    def validate_nome(self, nome: str) -> Any:
        objeto_nao_deve_ter_duplicidade(TipoAlimentacao, 'Já existe um tipo de alimento com este nome: {}'.format(nome),
                                        nome=nome)
        return nome

    class Meta:
        model = TipoAlimentacao
        fields = ['uuid', 'nome']


class InversaoCardapioSerializer(serializers.ModelSerializer):

    def validate_cardapio_de(self, cardapio_de):
        cardapio_existe(cardapio_de)
        cardapio_antigo(cardapio_de)
        return cardapio_de

    def validate_cardapio_para(self, cardapio_para):
        cardapio_existe(cardapio_para)
        cardapio_antigo(cardapio_para)
        return cardapio_para

    def validate(self, attrs):
        de = attrs.get('cardapio_de')
        para = attrs.get('cardapio_para')
        valida_cardapio_de_para(de, para)
        return attrs

    class Meta:
        model = InversaoCardapio
        fields = ['uuid', 'descricao', 'criado_em', 'cardapio_de', 'cardapio_para', 'escola']


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
