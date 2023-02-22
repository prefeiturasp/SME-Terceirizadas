import json

from rest_framework import status

from sme_terceirizadas.dados_comuns import constants
from sme_terceirizadas.pre_recebimento.models import Cronograma, EmbalagemQld, Laboratorio


def test_url_endpoint_cronograma(client_autenticado_codae_dilog, armazem, contrato, empresa):
    data = {
        'armazem': str(armazem.uuid),
        'contrato': str(contrato.uuid),
        'empresa': str(empresa.uuid),
        'cadastro_finalizado': False,
        'etapas': [
            {
                'numero_empenho': '123456789'
            },
            {
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
    response = client_autenticado_codae_dilog.post(
        '/cronogramas/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = Cronograma.objects.last()
    assert obj.contrato == contrato


def test_url_lista_etapas_authorized_numeros(client_autenticado_codae_dilog):
    response = client_autenticado_codae_dilog.get('/cronogramas/opcoes-etapas/')
    assert response.status_code == status.HTTP_200_OK


def test_url_list_cronogramas(client_autenticado_codae_dilog):
    response = client_autenticado_codae_dilog.get('/cronogramas/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_fornecedor_assina_cronograma_authorized(client_autenticado_fornecedor, cronograma_recebido):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_fornecedor.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/fornecedor-assina-cronograma/', data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.get(uuid=cronograma_recebido.uuid)
    assert obj.status == 'ASSINADO_FORNECEDOR'


def test_url_fornecedor_confirma_cronograma_erro_transicao_estado(client_autenticado_fornecedor, cronograma):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_fornecedor.patch(
        f'/cronogramas/{cronograma.uuid}/fornecedor-assina-cronograma/', data,
        content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_fornecedor_confirma_not_authorized(client_autenticado_codae_dilog, cronograma_recebido):
    response = client_autenticado_codae_dilog.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/fornecedor-assina-cronograma/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_list_rascunhos_cronogramas(client_autenticado_codae_dilog):
    response = client_autenticado_codae_dilog.get('/cronogramas/rascunhos/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'results' in json


def test_url_endpoint_cronograma_editar(client_autenticado_codae_dilog, cronograma_rascunho, contrato, empresa):
    data = {
        'empresa': str(empresa.uuid),
        'contrato': str(contrato.uuid),
        'cadastro_finalizado': True,
        'etapas': [
            {
                'numero_empenho': '123456789'
            },
            {
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
    response = client_autenticado_codae_dilog.put(
        f'/cronogramas/{cronograma_rascunho.uuid}/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.last()
    assert cronograma_rascunho.status == 'RASCUNHO'
    assert obj.status == 'ENVIADO_AO_FORNECEDOR'


def test_url_endpoint_laboratorio(client_autenticado_qualidade):
    data = {
        'contatos': [
            {
                'nome': 'TEREZA',
                'telefone': '8135431540',
                'email': 'maxlab@max.com',
            }
        ],
        'nome': 'Laboratorio de testes maiusculo',
        'cnpj': '10359359000154',
        'cep': '53600000',
        'logradouro': 'OLIVEIR',
        'numero': '120',
        'complemento': '',
        'bairro': 'CENTRO',
        'cidade': 'IGARASSU',
        'estado': 'PE',
        'credenciado': True
    }
    response = client_autenticado_qualidade.post(
        '/laboratorios/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = Laboratorio.objects.last()
    assert obj.nome == 'LABORATORIO DE TESTES MAIUSCULO'


def test_url_laboratorios_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/laboratorios/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_laboratorio_editar(client_autenticado_qualidade, laboratorio):
    data = {
        'contatos': [
            {
                'nome': 'TEREZA',
                'telefone': '8135431540',
                'email': 'maxlab@max.com',
            }
        ],
        'nome': 'Laboratorio de testes maiusculo',
        'cnpj': '10359359000154',
        'cep': '53600000',
        'logradouro': 'OLIVEIR',
        'numero': '120',
        'complemento': '',
        'bairro': 'CENTRO',
        'cidade': 'IGARASSU',
        'estado': 'PE',
        'credenciado': True
    }
    response = client_autenticado_qualidade.put(
        f'/laboratorios/{laboratorio.uuid}/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_200_OK
    obj = Laboratorio.objects.last()
    assert obj.nome == 'LABORATORIO DE TESTES MAIUSCULO'


def test_url_lista_laboratorios_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/laboratorios/lista-laboratorios/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_embalagem_create(client_autenticado_qualidade):
    data = {
        'nome': 'fardo',
        'abreviacao': 'FD'
    }
    response = client_autenticado_qualidade.post(
        '/embalagens/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = EmbalagemQld.objects.last()
    assert obj.nome == 'FARDO'


def test_url_embalagen_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/embalagens/')
    assert response.status_code == status.HTTP_200_OK


def test_url_lista_nomes_embalagens_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/embalagens/lista-nomes-embalagens/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_embalagem_update(client_autenticado_qualidade, emabalagem_qld):
    data = {
        'nome': 'saco',
        'abreviacao': 'SC'
    }
    response = client_autenticado_qualidade.put(
        f'/embalagens/{emabalagem_qld.uuid}/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_200_OK
    obj = EmbalagemQld.objects.last()
    assert obj.nome == 'SACO'


def test_url_perfil_cronograma_assina_cronograma_authorized(client_autenticado_dilog_cronograma,
                                                            cronograma_assinado_fornecedor):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dilog_cronograma.patch(
        f'/cronogramas/{cronograma_assinado_fornecedor.uuid}/cronograma-assina/', data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.get(uuid=cronograma_assinado_fornecedor.uuid)
    assert obj.status == 'ASSINADO_CRONOGRAMA'


def test_url_perfil_cronograma_assina_cronograma_erro_senha(client_autenticado_dilog_cronograma,
                                                            cronograma_assinado_fornecedor):
    data = json.dumps({'password': 'senha_errada'})
    response = client_autenticado_dilog_cronograma.patch(
        f'/cronogramas/{cronograma_assinado_fornecedor.uuid}/cronograma-assina/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_perfil_cronograma_assina_cronograma_erro_transicao_estado(client_autenticado_dilog_cronograma, cronograma):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dilog_cronograma.patch(
        f'/cronogramas/{cronograma.uuid}/cronograma-assina/', data,
        content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_perfil_cronograma_assina_not_authorized(client_autenticado_dilog, cronograma_recebido):
    response = client_autenticado_dilog.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/cronograma-assina/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_dinutre_assina_cronograma_authorized(client_autenticado_dinutre_diretoria,
                                                  cronograma_assinado_perfil_cronograma):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_perfil_cronograma.uuid}/dinutre-assina/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.get(uuid=cronograma_assinado_perfil_cronograma.uuid)
    assert obj.status == 'ASSINADO_DINUTRE'


def test_url_dinutre_assina_cronograma_erro_senha(client_autenticado_dinutre_diretoria,
                                                  cronograma_assinado_fornecedor):
    data = json.dumps({'password': 'senha_errada'})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_fornecedor.uuid}/dinutre-assina/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_dinutre_assina_cronograma_erro_transicao_estado(client_autenticado_dinutre_diretoria,
                                                             cronograma):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{cronograma.uuid}/dinutre-assina/', data,
        content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_dinutre_assina_cronograma_not_authorized(client_autenticado_dilog,
                                                      cronograma_recebido):
    response = client_autenticado_dilog.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/dinutre-assina/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_dashboard_painel_usuario_dinutre(client_autenticado_dinutre_diretoria,
                                              cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard/'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 2
    assert response.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert len(response.json()['results'][0]['dados']) == 3
    assert response.json()['results'][1]['status'] == 'ASSINADO_DINUTRE'
    assert len(response.json()['results'][1]['dados']) == 2


def test_url_dashboard_painel_usuario_dinutre_com_paginacao(client_autenticado_dinutre_diretoria,
                                                            cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard/?status=ASSINADO_CRONOGRAMA&limit=2&offset=0'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1
    assert response.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert response.json()['results'][0]['total'] == 3
    assert len(response.json()['results'][0]['dados']) == 2


def test_url_dashboard_com_filtro_painel_usuario_dinutre(client_autenticado_dinutre_diretoria,
                                                         cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/'
    )
    filtro1 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?nome_produto=Arroz'
    )
    filtro2 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?numero_cronograma=003/2023'
    )
    filtro3 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?nome_fornecedor=Alimentos'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 2
    assert response.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert len(response.json()['results'][0]['dados']) == 3
    assert response.json()['results'][1]['status'] == 'ASSINADO_DINUTRE'
    assert len(response.json()['results'][1]['dados']) == 2
    assert filtro1.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert len(filtro1.json()['results'][0]['dados']) == 1
    assert filtro1.json()['results'][1]['status'] == 'ASSINADO_DINUTRE'
    assert len(filtro1.json()['results'][1]['dados']) == 1
    assert filtro2.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert len(filtro2.json()['results'][0]['dados']) == 1
    assert filtro2.json()['results'][1]['status'] == 'ASSINADO_DINUTRE'
    assert len(filtro2.json()['results'][1]['dados']) == 0
    assert filtro3.json()['results'][0]['status'] == 'ASSINADO_CRONOGRAMA'
    assert len(filtro3.json()['results'][0]['dados']) == 3
    assert filtro3.json()['results'][1]['status'] == 'ASSINADO_DINUTRE'
    assert len(filtro3.json()['results'][1]['dados']) == 2
