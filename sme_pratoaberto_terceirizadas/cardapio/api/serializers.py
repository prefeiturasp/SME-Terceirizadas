from datetime import date

from rest_framework import serializers
from traitlets import Any

from sme_pratoaberto_terceirizadas.dados_comuns.validators import (nao_pode_ser_passado, nao_pode_ser_feriado, \
                                                                   objeto_nao_deve_ter_duplicidade, verificar_se_existe)
from sme_pratoaberto_terceirizadas.escola.api.serializers import EscolaSimplesSerializer
from .validators import cardapio_antigo
from ..models import *


class TipoAlimentacaoSerializer(serializers.ModelSerializer):

    def validate_nome(self, nome: str) -> Any:
        objeto_nao_deve_ter_duplicidade(TipoAlimentacao, 'Já existe um tipo de alimento com este nome: {}'.format(nome),
                                        nome=nome)
        return nome

    class Meta:
        model = TipoAlimentacao
        fields = ['uuid', 'nome']


class CardapioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cardapio
        fields = ['uuid', 'data']


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


class InversaoCardapioSerializer(serializers.ModelSerializer):
    cardapio_de = CardapioSimplesSerializer()
    cardapio_para = CardapioSimplesSerializer()
    escola = EscolaSimplesSerializer()

    def validate_cardapio_de(self, value):
        verificar_se_existe(Cardapio, uuid=value)
        cardapio_antigo(value)
        return value

    def validate_cardapio_para(self, value):
        verificar_se_existe(Cardapio, uuid=value)
        cardapio_antigo(value)
        return value

    # def validate(self, attrs):
    #     request = self._filtrar_requisicao(attrs)
    #     de = request.get('cardapio_de')
    #     para = request.get('cardapio_para')
    #     escola = request.get('escola')
    #     valida_cardapio_de_para(de, para)
    #     valida_duplicidade(de, para, escola)
    #     return attrs

    def _filtrar_requisicao(self, request):
        request['cardapio_de'] = Cardapio.objects.get(uuid=request.get('cardapio_de'))
        request['cardapio_para'] = Cardapio.objects.get(uuid=request.get('cardapio_para'))
        request['escola'] = Escola.objects.get(uuid=request.get('escola'))
        return request

    class Meta:
        model = InversaoCardapio
        fields = ['uuid', 'descricao', 'criado_em', 'cardapio_de', 'cardapio_para', 'escola']
