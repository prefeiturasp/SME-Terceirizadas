from rest_framework import status

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import InformativoPartindoDaEscolaWorkflow, PedidoAPartirDaEscolaWorkflow

from ..constants import (
    ENDPOINT_ALERGIAS_INTOLERANCIAS,
    ENDPOINT_CLASSIFICACOES_DIETA,
    ENDPOINT_MOTIVOS_NEGACAO,
    ENDPOINT_TIPOS_DIETA_ESPECIAL
)
from ..models import (
    AlergiaIntolerancia,
    ClassificacaoDieta,
    MotivoNegacao,
    TipoDieta
)


def testa_endpoint_lista(client_autenticado, endpoint, quantidade):
    response = client_autenticado.get(f'/{endpoint}/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json['results']) == quantidade


def test_url_endpoint_lista_alergias_intolerancias(client_autenticado,
                                                   alergias_intolerancias):
    testa_endpoint_lista(
        client_autenticado,
        ENDPOINT_ALERGIAS_INTOLERANCIAS,
        quantidade=2
    )


def test_url_endpoint_lista_classificacoes_dieta(client_autenticado,
                                                 classificacoes_dieta):
    testa_endpoint_lista(
        client_autenticado,
        ENDPOINT_CLASSIFICACOES_DIETA,
        quantidade=3
    )


def test_url_endpoint_lista_motivos_negacao(client_autenticado,
                                            motivos_negacao):
    testa_endpoint_lista(
        client_autenticado,
        ENDPOINT_MOTIVOS_NEGACAO,
        quantidade=4
    )


def test_url_endpoint_lista_tipos_dieta(client_autenticado,
                                        tipos_dieta):
    testa_endpoint_lista(
        client_autenticado,
        ENDPOINT_TIPOS_DIETA_ESPECIAL,
        quantidade=5
    )


def testa_endpoint_detalhe(client_autenticado, endpoint, modelo, tem_nome=False):
    obj = modelo.objects.first()
    response = client_autenticado.get(f'/{endpoint}/{obj.id}/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert obj.descricao == json['descricao']
    if tem_nome:
        assert obj.nome == json['nome']

def test_url_endpoint_detalhe_alergias_intolerancias(client_autenticado,
                                                     alergias_intolerancias):
    testa_endpoint_detalhe(
        client_autenticado,
        ENDPOINT_ALERGIAS_INTOLERANCIAS,
        AlergiaIntolerancia
    )


def test_url_endpoint_detalhe_classificacoes_dieta(client_autenticado,
                                                   classificacoes_dieta):
    testa_endpoint_detalhe(
        client_autenticado,
        ENDPOINT_CLASSIFICACOES_DIETA,
        ClassificacaoDieta,
        tem_nome=True
    )


def test_url_endpoint_detalhe_motivos_negacao(client_autenticado,
                                              motivos_negacao):
    testa_endpoint_detalhe(
        client_autenticado,
        ENDPOINT_MOTIVOS_NEGACAO,
        MotivoNegacao
    )


def test_url_endpoint_detalhe_tipos_dieta(client_autenticado,
                                          tipos_dieta):
    testa_endpoint_detalhe(
        client_autenticado,
        ENDPOINT_TIPOS_DIETA_ESPECIAL,
        TipoDieta
    )
