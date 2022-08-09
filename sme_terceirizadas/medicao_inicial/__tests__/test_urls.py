from rest_framework import status

from sme_terceirizadas.medicao_inicial.models import DiaSobremesaDoce


def test_url_endpoint_cria_dias_sobremesa_doce(client_autenticado_coordenador_codae):
    data = {
        'data': '2022-08-08',
        'tipo_unidades': ['1cc3253b-e297-42b3-8e57-ebfd115a1aba',
                          '40ee89a7-dc70-4abb-ae21-369c67f2b9e3',
                          'ac4858ff-1c11-41f3-b539-7a02696d6d1b']
    }
    response = client_autenticado_coordenador_codae.post(
        '/medicao-inicial/dias-sobremesa-doce/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert DiaSobremesaDoce.objects.count() == 3
    response = client_autenticado_coordenador_codae.get(
        '/medicao-inicial/dias-sobremesa-doce/?mes=8&ano=2022',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 3
    response = client_autenticado_coordenador_codae.get(
        '/medicao-inicial/dias-sobremesa-doce/?mes=9&ano=2022',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 0
    data = {
        'data': '2022-08-08',
        'tipo_unidades': []
    }
    response = client_autenticado_coordenador_codae.post(
        '/medicao-inicial/dias-sobremesa-doce/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert DiaSobremesaDoce.objects.count() == 0
