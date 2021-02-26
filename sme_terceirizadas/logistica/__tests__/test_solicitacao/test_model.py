import pytest
from django.contrib.auth import get_user_model

from ...models.solicitacao import SolicitacaoRemessa, SolicitacaoDeAlteracaoRequisicao

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_instance_model(solicitacao):
    model = solicitacao
    assert isinstance(model, SolicitacaoRemessa)
    assert model.cnpj
    assert model.numero_solicitacao
    assert model.status


def test_srt_model(solicitacao):
    assert solicitacao.__str__() == 'Solicitação: 559890 - Status: Aguardando envio'


def test_meta_model(solicitacao):
    assert solicitacao._meta.verbose_name == 'Solicitação Remessa'
    assert solicitacao._meta.verbose_name_plural == 'Solicitações Remessas'


def test_solicitacao_de_alteracao_requisicao_model(solicitacao_de_alteracao_requisicao):
    model = solicitacao_de_alteracao_requisicao
    assert isinstance(model, SolicitacaoDeAlteracaoRequisicao)


def test_srt_solicitacao_de_alteracao_requisicao_model(solicitacao_de_alteracao_requisicao):
    assert solicitacao_de_alteracao_requisicao.__str__() == 'Solicitação de alteração: 00000001-ALT'


def test_meta_solicitacao_de_alteracao_requisicao_model(solicitacao_de_alteracao_requisicao):
    assert solicitacao_de_alteracao_requisicao._meta.verbose_name == 'Solicitação de Alteração de Requisição'
    assert solicitacao_de_alteracao_requisicao._meta.verbose_name_plural == 'Solicitações de Alteração de Requisição'


def test_solicitacao_de_alteracao_requisicao_numero_solicitacao(solicitacao_de_alteracao_requisicao):
    assert solicitacao_de_alteracao_requisicao.numero_solicitacao == '00000001-ALT'
