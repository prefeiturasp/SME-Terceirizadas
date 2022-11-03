from rest_framework import status

from sme_terceirizadas.pre_recebimento.models import Cronograma


def test_url_endpoint_cronograma(client_autenticado_dilog):
    data = {
        'armazem': '3886c9f7-b897-4740-970d-659e4096a511',
        'contrato_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
        'contrato': '5678/2022',
        'cadastro_finalizado': False,
        'etapas': [
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '123456789'
            },
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '1891425',
                'etapa': 'Etapa 1'
            }
        ],
        'programacoes_de_recebimento': [
            {
                'data_programada': '22/08/2022 - Etapa 1 - Parte 1',
                'tipo_carga': 'PALETIZADA'
            }
        ]
    }
    response = client_autenticado_dilog.post(
        '/cronogramas/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = Cronograma.objects.last()
    assert obj.contrato == '5678/2022'


def test_url_lista_etapas_authorized_numeros(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/cronogramas/etapas/')
    assert response.status_code == status.HTTP_200_OK
