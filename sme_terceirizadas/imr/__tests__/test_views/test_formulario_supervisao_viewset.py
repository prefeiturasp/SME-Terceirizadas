import pytest
from rest_framework import status

from sme_terceirizadas.imr.api.viewsets import FormularioSupervisaoModelViewSet
from sme_terceirizadas.imr.models import FormularioSupervisao, PerfilDiretorSupervisao

pytestmark = pytest.mark.django_db


def test_get_categorias_nao_permitidas():
    view_instance = FormularioSupervisaoModelViewSet()

    # Teste para CEMEI
    categorias = view_instance._get_categorias_nao_permitidas("CEMEI")
    assert "LACTÁRIO" not in categorias
    assert "RESÍDUO DE ÓLEO UTILIZADO NA FRITURA" not in categorias

    # Teste para outro tipo de escola
    categorias = view_instance._get_categorias_nao_permitidas("EMEF")
    assert "LACTÁRIO" in categorias
    assert "RESÍDUO DE ÓLEO UTILIZADO NA FRITURA" not in categorias


def test_tipos_ocorrencias(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    edital_factory,
    categoria_ocorrencia_factory,
    tipo_ocorrencia_factory,
    escola_factory,
    tipo_unidade_escolar_factory,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao
    edital = edital_factory.create()

    categoria = categoria_ocorrencia_factory.create(
        perfis=[PerfilDiretorSupervisao.SUPERVISAO], posicao=1
    )
    categoria_lactario = categoria_ocorrencia_factory.create(
        nome="LACTÁRIO", perfis=[PerfilDiretorSupervisao.SUPERVISAO], posicao=2
    )
    tipo_unidade_emef = tipo_unidade_escolar_factory.create(iniciais="EMEF")
    escola_emef = escola_factory.create(tipo_unidade=tipo_unidade_emef)
    tipo_unidade_cemei = tipo_unidade_escolar_factory.create(iniciais="CEMEI")
    escola_cemei = escola_factory.create(tipo_unidade=tipo_unidade_cemei)

    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao="Ocorrencia 1",
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria,
        posicao=1,
    )
    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao="Ocorrencia 2",
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria,
        posicao=2,
    )
    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao="Ocorrencia 3",
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria_lactario,
        posicao=3,
    )

    response = client.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}&escola_uuid={escola_emef.uuid}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert len(response_data) == 2
    assert response_data[0]["descricao"] == "Ocorrencia 1"
    assert response_data[1]["descricao"] == "Ocorrencia 2"

    response_cemei = client.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}&escola_uuid={escola_cemei.uuid}"
    )

    assert response_cemei.status_code == status.HTTP_200_OK

    response_cemei_data = response_cemei.json()

    assert len(response_cemei_data) == 3
    assert response_cemei_data[0]["descricao"] == "Ocorrencia 1"
    assert response_cemei_data[1]["descricao"] == "Ocorrencia 2"
    assert response_cemei_data[2]["descricao"] == "Ocorrencia 3"

    client.logout()


def test_tipos_ocorrencias_edital_ou_escola_UUID_invalido(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    escola_factory,
    edital_factory,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao
    edital = edital_factory.create()
    escola = escola_factory.create()

    response = client.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid=&escola_uuid={escola.uuid}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}&escola_uuid="
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    client.logout()


def test_url_lista_formularios_supervisao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao
    response = client.get("/imr/formulario-supervisao/")
    assert response.status_code == status.HTTP_200_OK


def test_url_dashboard_supervisao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    formulario_supervisao_factory,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao

    formulario_supervisao_factory.create()
    formulario_supervisao_factory.create(formulario_base__usuario=usuario)
    formulario_supervisao_factory.create(formulario_base__usuario=usuario)

    formulario_supervisao_factory.create(
        status=FormularioSupervisao.workflow_class.NUTRIMANIFESTACAO_A_VALIDAR
    )
    formulario_supervisao_factory.create(
        formulario_base__usuario=usuario,
        status=FormularioSupervisao.workflow_class.NUTRIMANIFESTACAO_A_VALIDAR,
    )
    formulario_supervisao_factory.create(
        formulario_base__usuario=usuario,
        status=FormularioSupervisao.workflow_class.NUTRIMANIFESTACAO_A_VALIDAR,
    )

    response = client.get("/imr/formulario-supervisao/dashboard/")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]

    em_preenchimento = next(
        result
        for result in results
        if result["status"] == FormularioSupervisao.workflow_class.EM_PREENCHIMENTO
    )
    assert em_preenchimento["total"] == 2

    nutrimanifestacao_a_validar = next(
        result
        for result in results
        if result["status"]
        == FormularioSupervisao.workflow_class.NUTRIMANIFESTACAO_A_VALIDAR
    )
    assert nutrimanifestacao_a_validar["total"] == 2

    total = next(
        result for result in results if result["status"] == "TODOS_OS_RELATORIOS"
    )
    assert total["total"] == 4
