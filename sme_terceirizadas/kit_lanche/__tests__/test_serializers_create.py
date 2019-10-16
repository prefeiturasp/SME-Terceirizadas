# SolicitacaoKitLancheAvulsaCreationSerializer
import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

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
    qtd_alunos_escola, qtd_alunos_pedido, dia, confirmar = kits_avulsos_param_erro_serializer
    serializer_obj = SolicitacaoKitLancheAvulsaCreationSerializer()
    escola = mommy.make('Escola', quantidade_alunos=qtd_alunos_escola)

    attrs = dict(quantidade_alunos=qtd_alunos_pedido,
                 escola=escola,
                 confirmar=confirmar,
                 solicitacao_kit_lanche=dict(data=dia))
    err1 = 'A quantidade de alunos informados para o evento excede a quantidade de alunos matriculados na escola'
    err2 = 'Não pode ser no passado'
    err3 = 'Deve pedir com pelo menos 2 dias úteis de antecedência'
    error_regex = fr'({err1}|{err2}|{err3})'
    with pytest.raises(ValidationError, match=error_regex):
        response = serializer_obj.validate(attrs=attrs)
