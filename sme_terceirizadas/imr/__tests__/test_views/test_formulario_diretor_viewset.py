import json
import uuid

import pytest
from rest_framework import status

from sme_terceirizadas.imr.models import FormularioOcorrenciasBase

pytestmark = pytest.mark.django_db


def test_formulario_diretor(
    client_autenticado_diretor_escola,
    escola,
    solicitacao_medicao_inicial_factory,
    tipo_resposta_modelo_factory,
    tipo_pergunta_parametrizacao_ocorrencia_factory,
    tipo_ocorrencia_factory,
    parametrizacao_ocorrencia_factory,
):
    solicitacao_medicao_inicial = solicitacao_medicao_inicial_factory(escola=escola)

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
        "datas": ["07/06/2024", "08/06/2024"],
        "solicitacao_medicao_inicial": str(solicitacao_medicao_inicial.uuid),
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

    response = client_autenticado_diretor_escola["client"].post(
        f"/imr/formulario-diretor/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["solicitacao_medicao_inicial"] == str(solicitacao_medicao_inicial.uuid)

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

    instance = FormularioOcorrenciasBase.objects.get(data="2024-06-08")
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


def test_formulario_diretor_erro_parametrizacao_uuid(
    client_autenticado_diretor_escola,
    escola,
    solicitacao_medicao_inicial_factory,
    tipo_resposta_modelo_factory,
    tipo_pergunta_parametrizacao_ocorrencia_factory,
    tipo_ocorrencia_factory,
    parametrizacao_ocorrencia_factory,
):
    solicitacao_medicao_inicial = solicitacao_medicao_inicial_factory(escola=escola)

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
        "datas": ["07/06/2024", "08/06/2024"],
        "solicitacao_medicao_inicial": str(solicitacao_medicao_inicial.uuid),
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

    response = client_autenticado_diretor_escola["client"].post(
        f"/imr/formulario-diretor/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": f"ParametrizacaoOcorrencia com o UUID {str(uuid_incorreto)} não foi encontrada"
    }
