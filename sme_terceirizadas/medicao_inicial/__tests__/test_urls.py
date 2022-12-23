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
        '/medicao-inicial/dias-sobremesa-doce/lista-dias/?mes=8&ano=2022'
        '&escola_uuid=95ad02fb-d746-4e0c-95f4-0181a99bc192',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == ['2022-08-08']

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


def test_url_endpoint_list_dias_erro(client_autenticado_coordenador_codae):
    response = client_autenticado_coordenador_codae.get(
        '/medicao-inicial/dias-sobremesa-doce/lista-dias/?mes=8&ano=2022'
        '&escola_uuid=95ad02fb-d746-4e0c-95f4-0181a99bc193',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_endpoint_solicitacao_medicao_inicial(client_autenticado_da_escola,
                                                  escola, solicitacao_medicao_inicial,
                                                  solicitacao_medicao_inicial_sem_arquivo,
                                                  responsavel, tipo_contagem_alimentacao):
    response = client_autenticado_da_escola.get(
        f'/medicao-inicial/solicitacao-medicao-inicial/?escola={escola.uuid}&mes=09&ano=2022',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    data_create = {
        'ano': 2022,
        'mes': 11,
        'escola': escola.uuid,
        'responsaveis': [{
            'nome': responsavel.nome,
            'rf': responsavel.rf
        }],
        'tipo_contagem_alimentacoes': tipo_contagem_alimentacao.uuid
    }
    response = client_autenticado_da_escola.post(
        f'/medicao-inicial/solicitacao-medicao-inicial/',
        content_type='application/json',
        data=data_create
    )
    assert response.status_code == status.HTTP_201_CREATED
    data_update = {
        'escola': str(escola.uuid),
        'responsaveis': [{
            'nome': 'tester_updated',
            'rf': str(responsavel.rf)
        }],
        'tipo_contagem_alimentacoes': str(tipo_contagem_alimentacao.uuid),
        'com_ocorrencias': True
    }
    response = client_autenticado_da_escola.patch(
        f'/medicao-inicial/solicitacao-medicao-inicial/{solicitacao_medicao_inicial_sem_arquivo.uuid}/',
        content_type='application/json',
        data=data_update
    )
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_valores_medicao(client_autenticado_da_escola, solicitacao_medicao_inicial):
    url = '/medicao-inicial/valores-medicao/?nome_periodo_escolar=MANHA'
    url += f'&uuid_solicitacao_medicao={solicitacao_medicao_inicial.uuid}'
    response = client_autenticado_da_escola.get(
        url,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


def test_url_endpoint_medicao(client_autenticado_da_escola,
                              solicitacao_medicao_inicial,
                              periodo_escolar, categoria_medicao, medicao):
    data = {
        'periodo_escolar': periodo_escolar.nome,
        'solicitacao_medicao_inicial': solicitacao_medicao_inicial.uuid,
        'valores_medicao': [{
            'categoria_medicao': categoria_medicao.id,
            'dia': '01',
            'nome_campo': 'repeticao_refeicao',
            'tipo_alimentacao': '',
            'valor': '100'
        }]
    }
    response = client_autenticado_da_escola.post(
        '/medicao-inicial/medicao/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    response = client_autenticado_da_escola.patch(
        f'/medicao-inicial/medicao/{medicao.uuid}/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_200_OK
    data_valor_0 = {
        'periodo_escolar': periodo_escolar.nome,
        'solicitacao_medicao_inicial': solicitacao_medicao_inicial.uuid,
        'valores_medicao': [{
            'categoria_medicao': categoria_medicao.id,
            'dia': '01',
            'nome_campo': 'repeticao_refeicao',
            'tipo_alimentacao': '',
            'valor': 0
        }]
    }
    response = client_autenticado_da_escola.patch(
        f'/medicao-inicial/medicao/{medicao.uuid}/',
        content_type='application/json',
        data=data_valor_0
    )
    assert response.status_code == status.HTTP_200_OK
