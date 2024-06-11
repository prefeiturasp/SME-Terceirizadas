import json
import uuid

import pytest
from rest_framework import status

from sme_terceirizadas.imr.models import (
    FormularioOcorrenciasBase,
    PerfilDiretorSupervisao,
)

pytestmark = pytest.mark.django_db


def test_formulario_supervisao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    escola,
    tipo_ocorrencia_factory,
):
    tipo_ocorrencia_1 = tipo_ocorrencia_factory.create()
    tipo_ocorrencia_2 = tipo_ocorrencia_factory.create()

    payload = {
        "data": "2024-05-15",
        "escola": str(escola.uuid),
        "maior_frequencia_no_periodo": 6,
        "ocorrencias_nao_se_aplica": [
            {
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "descricao": "Não se aplica",
            },
            {
                "tipo_ocorrencia": str(tipo_ocorrencia_2.uuid),
                "descricao": "Não se aplica v2",
            },
        ],
    }

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/rascunho-formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = response.json()

    instance = FormularioOcorrenciasBase.objects.get(uuid=data["formulario_base"])

    assert response.status_code == status.HTTP_201_CREATED
    assert data["escola"] == str(escola.uuid)
    assert data["status"] == "EM_PREENCHIMENTO"
    assert data["maior_frequencia_no_periodo"] == 6
    assert instance.respostas_nao_se_aplica.count() == 2


def test_formulario_supervisao_tipo_ocorrencia_nao_existe(
    client_autenticado_vinculo_coordenador_supervisao_nutricao, escola
):
    payload = {
        "data": "2024-05-15",
        "escola": str(escola.uuid),
        "ocorrencias_nao_se_aplica": [
            {
                "tipo_ocorrencia": "2b7a2217-1743-4bcd-8879-cf8e16e34fa6",
                "descricao": "",
            },
        ],
    }
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/rascunho-formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "ocorrencias_nao_se_aplica": {
            "tipo_ocorrencia": [
                "Objeto com uuid=2b7a2217-1743-4bcd-8879-cf8e16e34fa6 não existe."
            ]
        }
    }


def test_tipos_ocorrencias(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    edital_factory,
    categoria_ocorrencia_factory,
    tipo_ocorrencia_factory,
):
    edital = edital_factory.create()

    categoria = categoria_ocorrencia_factory.create(
        perfis=[PerfilDiretorSupervisao.SUPERVISAO]
    )

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

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert len(response_data) == 2
    assert response_data[0]["descricao"] == "Ocorrencia 1"
    assert response_data[1]["descricao"] == "Ocorrencia 2"

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()


def test_tipos_ocorrencias_edital_UUID_invalido(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
):
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid="
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()


def test_url_lista_formularios_supervisao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
):
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        "/imr/formulario-supervisao/"
    )
    assert response.status_code == status.HTTP_200_OK


def test_formulario_supervisao_respostas_nao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    escola,
    tipo_resposta_modelo_factory,
    tipo_pergunta_parametrizacao_ocorrencia_factory,
    tipo_ocorrencia_factory,
    parametrizacao_ocorrencia_factory,
):
    tipo_resposta_campo_simples = tipo_resposta_modelo_factory(
        nome="RespostaCampoTextoSimples"
    )
    tipo_pergunta_parametrizacao_ocorrencia_texto_simples = (
        tipo_pergunta_parametrizacao_ocorrencia_factory(
            nome="Campo de Texto Simples", tipo_resposta=tipo_resposta_campo_simples
        )
    )

    tipo_resposta_campo_numerico = tipo_resposta_modelo_factory(
        nome="RespostaCampoNumerico"
    )
    tipo_pergunta_parametrizacao_ocorrencia_campo_numerico = (
        tipo_pergunta_parametrizacao_ocorrencia_factory(
            nome="Campo Numérico", tipo_resposta=tipo_resposta_campo_numerico
        )
    )

    tipo_ocorrencia_1 = tipo_ocorrencia_factory.create()
    parametrizacao_ocorrencia_1 = parametrizacao_ocorrencia_factory(
        tipo_ocorrencia=tipo_ocorrencia_1,
        tipo_pergunta=tipo_pergunta_parametrizacao_ocorrencia_texto_simples,
        titulo="Qual uniforme faltou?",
    )
    parametrizacao_ocorrencia_2 = parametrizacao_ocorrencia_factory(
        tipo_ocorrencia=tipo_ocorrencia_1,
        tipo_pergunta=tipo_pergunta_parametrizacao_ocorrencia_campo_numerico,
        titulo="Quantos uniformes faltaram?",
    )

    payload = {
        "data": "07/06/2024",
        "escola": str(escola.uuid),
        "ocorrencias": [
            {
                "grupo": 1,
                "parametrizacao": str(parametrizacao_ocorrencia_1.uuid),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": "calça",
            },
            {
                "grupo": 2,
                "parametrizacao": str(parametrizacao_ocorrencia_1.uuid),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": "camisa",
            },
            {
                "grupo": 2,
                "parametrizacao": str(parametrizacao_ocorrencia_2.uuid),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": 10,
            },
        ],
    }

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    instance = FormularioOcorrenciasBase.objects.get(data="2024-06-07")
    assert instance.respostas_campo_texto_simples.count() == 2
    assert (
        instance.respostas_campo_texto_simples.filter(resposta="calça").exists() is True
    )
    assert (
        instance.respostas_campo_texto_simples.filter(
            resposta="camisa", grupo=2
        ).exists()
        is True
    )
    assert instance.respostas_campo_numerico.count() == 1
    assert instance.respostas_campo_numerico.filter(resposta=10).exists() is True


def test_formulario_supervisao_erro_parametrizacao_uuid(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    escola,
    tipo_resposta_modelo_factory,
    tipo_pergunta_parametrizacao_ocorrencia_factory,
    tipo_ocorrencia_factory,
    parametrizacao_ocorrencia_factory,
):
    tipo_resposta_campo_simples = tipo_resposta_modelo_factory(
        nome="RespostaCampoTextoSimples"
    )
    tipo_pergunta_parametrizacao_ocorrencia_texto_simples = (
        tipo_pergunta_parametrizacao_ocorrencia_factory(
            nome="Campo de Texto Simples", tipo_resposta=tipo_resposta_campo_simples
        )
    )

    tipo_ocorrencia_1 = tipo_ocorrencia_factory.create()
    parametrizacao_ocorrencia_1 = parametrizacao_ocorrencia_factory(
        tipo_ocorrencia=tipo_ocorrencia_1,
        tipo_pergunta=tipo_pergunta_parametrizacao_ocorrencia_texto_simples,
        titulo="Qual uniforme faltou?",
    )

    uuid_incorreto = uuid.uuid4()

    payload = {
        "data": "07/06/2024",
        "escola": str(escola.uuid),
        "ocorrencias": [
            {
                "grupo": 1,
                "parametrizacao": str(parametrizacao_ocorrencia_1.uuid),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": "calça",
            },
            {
                "grupo": 2,
                "parametrizacao": str(parametrizacao_ocorrencia_1.uuid),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": "camisa",
            },
            {
                "grupo": 2,
                "parametrizacao": str(uuid_incorreto),
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "resposta": 10,
            },
        ],
    }

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": f"ParametrizacaoOcorrencia com o UUID {str(uuid_incorreto)} não foi encontrada"
    }
