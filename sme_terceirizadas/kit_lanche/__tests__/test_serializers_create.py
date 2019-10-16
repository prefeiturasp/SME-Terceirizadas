# SolicitacaoKitLancheAvulsaCreationSerializer
import datetime
import random

import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from sme_terceirizadas.kit_lanche.api.serializers.serializers_create import \
    SolicitacaoKitLancheUnificadaCreationSerializer
from sme_terceirizadas.kit_lanche.models import SolicitacaoKitLancheAvulsa, SolicitacaoKitLanche
from ..api.serializers.serializers_create import SolicitacaoKitLancheAvulsaCreationSerializer

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-16')
def test_kit_lanche_avulso_serializer_validators():
    serializer_obj = SolicitacaoKitLancheAvulsaCreationSerializer()
    escola = mommy.make('Escola', quantidade_alunos=778)
    attrs = dict(quantidade_alunos=777,
                 escola=escola,
                 confirmar=True,
                 solicitacao_kit_lanche=dict(data=datetime.date(2019, 10, 18)))
    response = serializer_obj.validate(attrs=attrs)
    assert response == attrs


@freeze_time('2019-10-16')
def test_kit_lanche_avulso_serializer_validators_error(kits_avulsos_param_erro_serializer):
    qtd_alunos_escola, qtd_alunos_pedido, dia, confirmar, erro_esperado = kits_avulsos_param_erro_serializer
    serializer_obj = SolicitacaoKitLancheAvulsaCreationSerializer()
    escola = mommy.make('Escola', quantidade_alunos=qtd_alunos_escola)

    attrs = dict(quantidade_alunos=qtd_alunos_pedido,
                 escola=escola,
                 confirmar=confirmar,
                 solicitacao_kit_lanche=dict(data=dia))
    with pytest.raises(ValidationError, match=erro_esperado):
        response = serializer_obj.validate(attrs=attrs)


@freeze_time('2019-10-16')
def test_kit_lanche_avulso_serializer_creators(kits_avulsos_param_serializer):
    qtd_alunos_escola, quantidade_alunos_pedido, data = kits_avulsos_param_serializer

    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    serializer_obj = SolicitacaoKitLancheAvulsaCreationSerializer(context={'request': FakeObject})
    escola = mommy.make('Escola', quantidade_alunos=qtd_alunos_escola)
    validated_data_create = dict(quantidade_alunos=quantidade_alunos_pedido,
                                 escola=escola,
                                 solicitacao_kit_lanche=dict(data=data))

    serializer_obj.validate(attrs=validated_data_create)

    response_created = serializer_obj.create(validated_data=validated_data_create)
    assert isinstance(response_created, SolicitacaoKitLancheAvulsa)
    assert response_created.criado_por == FakeObject.user
    assert response_created.escola == escola
    assert response_created.solicitacao_kit_lanche.data == data
    assert response_created.quantidade_alunos == quantidade_alunos_pedido
    assert response_created.status == SolicitacaoKitLancheAvulsa.workflow_class.RASCUNHO

    data2 = data + datetime.timedelta(days=1)
    validated_data_update = dict(quantidade_alunos=quantidade_alunos_pedido,
                                 escola=escola,
                                 solicitacao_kit_lanche=dict(data=data2))

    serializer_obj.validate(attrs=validated_data_update)

    response_updated = serializer_obj.update(instance=response_created, validated_data=validated_data_update)
    assert isinstance(response_updated, SolicitacaoKitLancheAvulsa)
    assert response_created.solicitacao_kit_lanche.data == data2


@freeze_time('2019-10-16')
def test_kit_lanche_unificado_serializer_validators_lista_igual(kits_unificados_param_serializer):
    serializer_obj = SolicitacaoKitLancheUnificadaCreationSerializer()
    kits = mommy.make('KitLanche', _quantity=3)
    qtd_alunos_escola, quantidade_alunos_pedido, data = kits_unificados_param_serializer
    escola = mommy.make('Escola', nome='teste', quantidade_alunos=qtd_alunos_escola)
    escola_quantidades = []
    for i in range(3):
        eq = mommy.make('EscolaQuantidade', quantidade_alunos=quantidade_alunos_pedido)
        escola_quantidades.append(dict(quantidade_alunos=eq.quantidade_alunos,
                                       kits=[],
                                       escola=escola))

    lista_kit_lanche_igual = True
    attrs = dict(lista_kit_lanche_igual=lista_kit_lanche_igual,
                 escolas_quantidades=escola_quantidades,
                 solicitacao_kit_lanche=dict(data=data,
                                             kits=kits,
                                             tempo_passeio=SolicitacaoKitLanche.CINCO_A_SETE))
    response = serializer_obj.validate(data=attrs)
    assert response == attrs


@freeze_time('2019-10-16')
def test_kit_lanche_unificado_serializer_validators_lista_nao_igual(kits_unificados_param_serializer):
    serializer_obj = SolicitacaoKitLancheUnificadaCreationSerializer()
    qtd_alunos_escola, quantidade_alunos_pedido, data = kits_unificados_param_serializer

    escola = mommy.make('Escola', quantidade_alunos=qtd_alunos_escola)
    escola_quantidades = []
    for i in range(3):
        kits = mommy.make('KitLanche', _quantity=random.randint(1, 3))
        eq = mommy.make('EscolaQuantidade', quantidade_alunos=quantidade_alunos_pedido)
        escola_quantidades.append(dict(quantidade_alunos=eq.quantidade_alunos,
                                       kits=kits,
                                       escola=escola))

    lista_kit_lanche_igual = False
    attrs = dict(lista_kit_lanche_igual=lista_kit_lanche_igual,
                 escolas_quantidades=escola_quantidades,
                 solicitacao_kit_lanche=dict(data=data,
                                             kits=[],
                                             tempo_passeio=None))
    response = serializer_obj.validate(data=attrs)
    assert response == attrs
