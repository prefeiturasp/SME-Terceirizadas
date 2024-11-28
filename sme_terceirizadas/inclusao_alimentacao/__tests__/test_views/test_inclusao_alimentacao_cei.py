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


def test_get_solicitacoes_diretoria_regional(
    client_autenticado_vinculo_dre_inclusao,
    inclusao_alimentacao_da_cei_factory,
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory,
    escola,
    monkeypatch,
):
    monkeypatch.setattr(
        EOLService,
        "get_informacoes_escola_turma_aluno",
        lambda p1: mocked_informacoes_escola_turma_aluno(),
    )

    inclusao_alimentacao_da_cei = inclusao_alimentacao_da_cei_factory.create(
        escola=escola, rastro_lote=escola.lote, status="DRE_A_VALIDAR"
    )
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory.create(
        inclusao_alimentacao_da_cei=inclusao_alimentacao_da_cei,
    )

    response = client_autenticado_vinculo_dre_inclusao.get(
        f"/inclusoes-alimentacao-da-cei/pedidos-diretoria-regional/sem_filtro/?lote={escola.lote.uuid}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1


def test_get_solicitacoes_diretoria_regional_eol_exception(
    client_autenticado_vinculo_dre_inclusao,
    inclusao_alimentacao_da_cei_factory,
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory,
    escola,
):
    inclusao_alimentacao_da_cei = inclusao_alimentacao_da_cei_factory.create(
        escola=escola, rastro_lote=escola.lote, status="DRE_A_VALIDAR"
    )
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory.create(
        inclusao_alimentacao_da_cei=inclusao_alimentacao_da_cei,
    )

    response = client_autenticado_vinculo_dre_inclusao.get(
        f"/inclusoes-alimentacao-da-cei/pedidos-diretoria-regional/sem_filtro/?lote={escola.lote.uuid}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "API EOL com erro. Status: 404"}


def test_get_solicitacoes_codae_gestao_alimentacao(
    client_autenticado_vinculo_codae_inclusao,
    inclusao_alimentacao_da_cei_factory,
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory,
    escola,
    monkeypatch,
):
    monkeypatch.setattr(
        EOLService,
        "get_informacoes_escola_turma_aluno",
        lambda p1: mocked_informacoes_escola_turma_aluno(),
    )

    inclusao_alimentacao_da_cei = inclusao_alimentacao_da_cei_factory.create(
        escola=escola,
        rastro_dre=escola.diretoria_regional,
        rastro_lote=escola.lote,
        status="DRE_VALIDADO",
    )
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory.create(
        inclusao_alimentacao_da_cei=inclusao_alimentacao_da_cei,
    )

    response = client_autenticado_vinculo_codae_inclusao.get(
        f"/inclusoes-alimentacao-da-cei/pedidos-codae/sem_filtro/?lote={escola.lote.uuid}&diretoria_regional={escola.diretoria_regional.uuid}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1


def test_get_solicitacoes_codae_gestao_alimentacao_eol_exception(
    client_autenticado_vinculo_codae_inclusao,
    inclusao_alimentacao_da_cei_factory,
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory,
    escola,
):
    inclusao_alimentacao_da_cei = inclusao_alimentacao_da_cei_factory.create(
        escola=escola,
        rastro_dre=escola.diretoria_regional,
        rastro_lote=escola.lote,
        status="DRE_VALIDADO",
    )
    quantidade_de_alunos_por_faixa_etaria_da_inclusao_de_alimentacao_da_cei_factory.create(
        inclusao_alimentacao_da_cei=inclusao_alimentacao_da_cei,
    )

    response = client_autenticado_vinculo_codae_inclusao.get(
        f"/inclusoes-alimentacao-da-cei/pedidos-codae/sem_filtro/?lote={escola.lote.uuid}&diretoria_regional={escola.diretoria_regional.uuid}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "API EOL com erro. Status: 404"}
