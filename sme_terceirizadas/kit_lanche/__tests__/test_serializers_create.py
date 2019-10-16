# SolicitacaoKitLancheAvulsaCreationSerializer
import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from sme_terceirizadas.kit_lanche.models import SolicitacaoKitLancheAvulsa
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
