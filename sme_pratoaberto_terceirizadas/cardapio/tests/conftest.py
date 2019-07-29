import pytest
from rest_framework.test import APIClient
from model_mommy import mommy
from datetime import datetime, timedelta
from faker import Faker

from ..models import SuspensaoAlimentacao, InversaoCardapio, MotivoAlteracaoCardapio, AlteracaoCardapio, \
    SubstituicoesAlimentacaoNoPeriodoEscolar

from ..api.serializers.serializers import SuspensaoAlimentacaoSerializer, InversaoCardapioSerializer, \
    MotivoAlteracaoCardapioSerializer, AlteracaoCardapioSerializer, SubstituicoesAlimentacaoNoPeriodoEscolarSerializer

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def cardapio_valido():
    data = datetime.now() + timedelta(days=2)
    cardapio_valido = mommy.prepare('Cardapio', _save_related=True, id=1, data=data.date(),
                                    uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4b')
    return cardapio_valido


@pytest.fixture
def cardapio_valido2():
    data = datetime.now() + timedelta(days=4)
    cardapio_valido2 = mommy.prepare('Cardapio', _save_related=True, id=2, data=data.date(),
                                     uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4c')
    return cardapio_valido2


@pytest.fixture
def cardapio_invalido():
    cardapio_invalido = mommy.prepare('Cardapio', _save_related=True, id=3, data=datetime(2019, 7, 2).date(),
                                      uuid='7a4ec98a-18a8-4d0a-b722-1da8f99aaf4d')
    return cardapio_invalido


@pytest.fixture
def escola():
    escola = mommy.prepare('Escola', _save_related=True)
    return escola


@pytest.fixture
def inversao_cardapio_serializer():
    inversao_cardapio = mommy.make(InversaoCardapio)
    return InversaoCardapioSerializer(inversao_cardapio)


@pytest.fixture
def suspensao_alimentacao_serializer():
    suspensao_alimentacao = mommy.make(SuspensaoAlimentacao)
    return SuspensaoAlimentacaoSerializer(suspensao_alimentacao)


@pytest.fixture
def motivo_alteracao_cardapio():
    return mommy.make(MotivoAlteracaoCardapio, nome=fake.name())


@pytest.fixture
def motivo_alteracao_cardapio_serializer():
    motivo_alteracao_cardapio = mommy.make(MotivoAlteracaoCardapio)
    return MotivoAlteracaoCardapioSerializer(motivo_alteracao_cardapio)


@pytest.fixture
def alteracao_cardapio():
    return mommy.make(AlteracaoCardapio, observacao="teste")


@pytest.fixture
def substituicoes_alimentacao_periodo():
    alteracao_cardapio = mommy.make(AlteracaoCardapio, observacao="teste")
    return mommy.make(SubstituicoesAlimentacaoNoPeriodoEscolar, alteracao_cardapio=alteracao_cardapio)


@pytest.fixture
def alteracao_cardapio_serializer():
    alteracao_cardapio = mommy.make(AlteracaoCardapio)
    return AlteracaoCardapioSerializer(alteracao_cardapio)


@pytest.fixture
def substituicoes_alimentacao_no_periodo_escolar_serializer():
    substituicoes_alimentacao_no_periodo_escolar = mommy.make(SubstituicoesAlimentacaoNoPeriodoEscolar)
    return SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(substituicoes_alimentacao_no_periodo_escolar)

