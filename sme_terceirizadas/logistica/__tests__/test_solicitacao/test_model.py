import pytest
from django.contrib.auth import get_user_model

from ...models.solicitacao import SolicitacaoRemessa

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_instance_model(solicitacao):
    model = solicitacao
    assert isinstance(model, SolicitacaoRemessa)
    assert model.cnpj
    assert model.numero_solicitacao
    assert model.status


def test_srt_model(solicitacao):
    assert solicitacao.__str__() == 'Solicitação: 559890 - Status: AGUARDANDO_ENVIO'


def test_meta_modelo(solicitacao):
    assert solicitacao._meta.verbose_name == 'Solicitação Remessa'
    assert solicitacao._meta.verbose_name_plural == 'Solicitações Remessas'
