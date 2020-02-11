from rest_framework import status

from ..models import FaixaEtaria


def test_url_endpoint_cria_faixa_etaria(client_autenticado_coordenador_codae):
    response = client_autenticado_coordenador_codae.post('/faixas-etarias/', {'inicio': 3, 'fim': 7})
    assert response.status_code == status.HTTP_201_CREATED

    faixa = FaixaEtaria.objects.first()
    assert faixa.inicio == 3
    assert faixa.fim == 7


def test_url_endpoint_lista_faixas_etarias(client_autenticado_coordenador_codae, faixas_etarias):
    response = client_autenticado_coordenador_codae.get('/faixas-etarias/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json['count'] == 8
