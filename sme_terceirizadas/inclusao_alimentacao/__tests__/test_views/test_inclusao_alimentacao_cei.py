import pytest
from rest_framework import status

from sme_terceirizadas.dados_comuns.constants import SOLICITACOES_DO_USUARIO
from sme_terceirizadas.eol_servico.utils import EOLService
from sme_terceirizadas.escola.__tests__.conftest import (
    mocked_informacoes_escola_turma_aluno,
)
from sme_terceirizadas.perfil.models import Usuario

pytestmark = pytest.mark.django_db


def test_get_minhas_solicitacoes(
    client_autenticado_vinculo_escola_inclusao,
    inclusao_alimentacao_da_cei_factory,
    escola,
    monkeypatch,
):
    monkeypatch.setattr(
        EOLService,
        "get_informacoes_escola_turma_aluno",
        lambda p1: mocked_informacoes_escola_turma_aluno(),
    )
    user = Usuario.objects.get(
        id=client_autenticado_vinculo_escola_inclusao.session["_auth_user_id"]
    )
    inclusao_alimentacao_da_cei = inclusao_alimentacao_da_cei_factory.create(
        criado_por=user, escola=escola
    )
    assert inclusao_alimentacao_da_cei.status == "RASCUNHO"

    response = client_autenticado_vinculo_escola_inclusao.get(
        f"/inclusoes-alimentacao-da-cei/{SOLICITACOES_DO_USUARIO}/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1