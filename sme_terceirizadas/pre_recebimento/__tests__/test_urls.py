import json
import uuid

from django.conf import settings
from rest_framework import status

from sme_terceirizadas.dados_comuns import constants
from sme_terceirizadas.dados_comuns.fluxo_status import LayoutDeEmbalagemWorkflow
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import (
    CronogramaSimplesSerializer,
    NomeEAbreviacaoUnidadeMedidaSerializer
)
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    Laboratorio,
    LayoutDeEmbalagem,
    SolicitacaoAlteracaoCronograma,
    TipoEmbalagemQld,
    UnidadeMedida
)
from sme_terceirizadas.pre_recebimento.utils import LayoutDeEmbalagemPagination, UnidadeMedidaPagination


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


def test_url_list_cronogramas(client_autenticado_codae_dilog, cronogramas_multiplos_status_com_log):
    response = client_autenticado_codae_dilog.get('/cronogramas/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_list_cronogramas_fornecedor(client_autenticado_fornecedor):
    response = client_autenticado_fornecedor.get('/cronogramas/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_list_solicitacoes_alteracao_cronograma(client_autenticado_dilog_cronograma):
    response = client_autenticado_dilog_cronograma.get('/solicitacao-de-alteracao-de-cronograma/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_list_solicitacoes_alteracao_cronograma_fornecedor(client_autenticado_fornecedor):
    response = client_autenticado_fornecedor.get('/solicitacao-de-alteracao-de-cronograma/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_solicitacao_alteracao_fornecedor(client_autenticado_fornecedor, cronograma_assinado_perfil_dilog):
    data = {
        'cronograma': str(cronograma_assinado_perfil_dilog.uuid),
        'etapas': [
            {
                'numero_empenho': '43532542',
                'etapa': 'Etapa 4',
                'parte': 'Parte 2',
                'data_programada': '2023-06-03',
                'quantidade': 123,
                'total_embalagens': 333
            },
            {
                'etapa': 'Etapa 1',
                'parte': 'Parte 1',
                'data_programada': '2023-09-14',
                'quantidade': '0',
                'total_embalagens': 1
            }
        ],
        'justificativa': 'Teste'
    }
    response = client_autenticado_fornecedor.post(
        '/solicitacao-de-alteracao-de-cronograma/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = SolicitacaoAlteracaoCronograma.objects.last()
    assert obj.status == 'EM_ANALISE'


def test_url_solicitacao_alteracao_dilog(client_autenticado_dilog_cronograma, cronograma_assinado_perfil_dilog):
    data = {
        'cronograma': str(cronograma_assinado_perfil_dilog.uuid),
        'qtd_total_programada': 124,
        'etapas': [
            {
                'numero_empenho': '43532542',
                'etapa': 'Etapa 4',
                'parte': 'Parte 2',
                'data_programada': '2023-06-03',
                'quantidade': 123,
                'total_embalagens': 333
            },
            {
                'etapa': 'Etapa 1',
                'parte': 'Parte 1',
                'data_programada': '2023-09-14',
                'quantidade': 1,
                'total_embalagens': 1
            }
        ],
        'justificativa': 'Teste',
        'programacoes_de_recebimento': [
            {
                'data_programada': '14/09/2023 - Etapa 1 - Parte 1',
                'tipo_carga': 'PALETIZADA'
            }
        ]
    }

    response = client_autenticado_dilog_cronograma.post(
        '/solicitacao-de-alteracao-de-cronograma/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_201_CREATED
    obj = SolicitacaoAlteracaoCronograma.objects.last()
    assert obj.status == 'ALTERACAO_ENVIADA_FORNECEDOR'
    assert obj.qtd_total_programada == 124
    assert obj.programacoes_novas.count() > 0


def test_url_perfil_cronograma_ciente_alteracao_cronograma(client_autenticado_dilog_cronograma,
                                                           solicitacao_cronograma_em_analise):
    data = json.dumps({
        'justificativa_cronograma': 'teste justificativa',
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
    })
    response = client_autenticado_dilog_cronograma.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_em_analise.uuid}/cronograma-ciente/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = SolicitacaoAlteracaoCronograma.objects.get(uuid=solicitacao_cronograma_em_analise.uuid)
    assert obj.status == 'CRONOGRAMA_CIENTE'


def test_url_cronograma_ciente_erro_solicitacao_cronograma_invalida(client_autenticado_dilog_cronograma):
    response = client_autenticado_dilog_cronograma.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{uuid.uuid4()}/cronograma-ciente/',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_url_cronograma_ciente_erro_transicao_estado(
    client_autenticado_dilog_cronograma,
    solicitacao_cronograma_ciente
):
    data = json.dumps({
        'justificativa_cronograma': 'teste justificativa',
    })
    response = client_autenticado_dilog_cronograma.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_ciente.uuid}/cronograma-ciente/',
        data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_perfil_dinutre_aprova_alteracao_cronograma(client_autenticado_dinutre_diretoria,
                                                        solicitacao_cronograma_ciente):
    data = json.dumps({
        'aprovado': True
    })
    response = client_autenticado_dinutre_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_ciente.uuid}/analise-dinutre/',
        data, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    obj = SolicitacaoAlteracaoCronograma.objects.get(uuid=solicitacao_cronograma_ciente.uuid)
    assert obj.status == 'APROVADO_DINUTRE'


def test_url_perfil_dinutre_reprova_alteracao_cronograma(client_autenticado_dinutre_diretoria,
                                                         solicitacao_cronograma_ciente):
    data = json.dumps({
        'justificativa_dinutre': 'teste justificativa',
        'aprovado': False
    })
    response = client_autenticado_dinutre_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_ciente.uuid}/analise-dinutre/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = SolicitacaoAlteracaoCronograma.objects.get(uuid=solicitacao_cronograma_ciente.uuid)
    assert obj.status == 'REPROVADO_DINUTRE'


def test_url_analise_dinutre_erro_parametro_aprovado_invalida(
    client_autenticado_dinutre_diretoria,
    solicitacao_cronograma_ciente
):
    data = json.dumps({
        'justificativa_dilog': 'teste justificativa',
        'aprovado': ''
    })
    response = client_autenticado_dinutre_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_ciente.uuid}/analise-dinutre/',
        data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_analise_dinutre_erro_solicitacao_cronograma_invalido(client_autenticado_dinutre_diretoria):
    response = client_autenticado_dinutre_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{uuid.uuid4()}/analise-dinutre/',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_url_analise_dinutre_erro_transicao_estado(
    client_autenticado_dinutre_diretoria,
    solicitacao_cronograma_aprovado_dinutre
):
    data = json.dumps({
        'justificativa_dilog': 'teste justificativa',
        'aprovado': True
    })
    response = client_autenticado_dinutre_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_aprovado_dinutre.uuid}/analise-dinutre/',
        data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_perfil_dilog_aprova_alteracao_cronograma(client_autenticado_dilog_diretoria,
                                                      solicitacao_cronograma_aprovado_dinutre):
    data = json.dumps({
        'aprovado': True
    })
    response = client_autenticado_dilog_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_aprovado_dinutre.uuid}/analise-dilog/',
        data, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    obj = SolicitacaoAlteracaoCronograma.objects.get(uuid=solicitacao_cronograma_aprovado_dinutre.uuid)
    assert obj.status == 'APROVADO_DILOG'


def test_url_perfil_dilog_reprova_alteracao_cronograma(client_autenticado_dilog_diretoria,
                                                       solicitacao_cronograma_aprovado_dinutre):
    data = json.dumps({
        'justificativa_dilog': 'teste justificativa',
        'aprovado': False
    })
    response = client_autenticado_dilog_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_aprovado_dinutre.uuid}/analise-dilog/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = SolicitacaoAlteracaoCronograma.objects.get(uuid=solicitacao_cronograma_aprovado_dinutre.uuid)
    assert obj.status == 'REPROVADO_DILOG'


def test_url_analise_dilog_erro_solicitacao_cronograma_invalido(client_autenticado_dilog_diretoria):
    response = client_autenticado_dilog_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{uuid.uuid4()}/analise-dilog/',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_url_analise_dilog_erro_parametro_aprovado_invalida(
    client_autenticado_dilog_diretoria,
    solicitacao_cronograma_aprovado_dinutre
):
    data = json.dumps({
        'justificativa_dilog': 'teste justificativa',
        'aprovado': ''
    })
    response = client_autenticado_dilog_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_aprovado_dinutre.uuid}/analise-dilog/',
        data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_analise_dilog_erro_transicao_estado(
    client_autenticado_dilog_diretoria,
    solicitacao_cronograma_ciente
):
    data = json.dumps({
        'justificativa_dilog': 'teste justificativa',
        'aprovado': True
    })
    response = client_autenticado_dilog_diretoria.patch(
        f'/solicitacao-de-alteracao-de-cronograma/{solicitacao_cronograma_ciente.uuid}/analise-dilog/',
        data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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


def test_url_fornecedor_confirma_not_authorized(client_autenticado_fornecedor, cronograma_recebido):
    data = json.dumps({'password': 'senha-errada'})
    response = client_autenticado_fornecedor.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/fornecedor-assina-cronograma/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_fornecedor_assina_cronograma_erro_cronograma_invalido(client_autenticado_fornecedor):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_fornecedor.patch(
        f'/cronogramas/{uuid.uuid4()}/fornecedor-assina-cronograma/', data, content_type='application/json')
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_url_list_rascunhos_cronogramas(client_autenticado_codae_dilog):
    response = client_autenticado_codae_dilog.get('/cronogramas/rascunhos/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'results' in json


def test_url_endpoint_cronograma_editar(client_autenticado_codae_dilog, cronograma_rascunho, contrato, empresa):
    data = {
        'empresa': str(empresa.uuid),
        'contrato': str(contrato.uuid),
        'password': constants.DJANGO_ADMIN_PASSWORD,
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
    assert obj.status == 'ASSINADO_E_ENVIADO_AO_FORNECEDOR'


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


def test_url_lista_nomes_laboratorios_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/laboratorios/lista-nomes-laboratorios/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_embalagem_create(client_autenticado_qualidade):
    data = {
        'nome': 'fardo',
        'abreviacao': 'FD'
    }
    response = client_autenticado_qualidade.post(
        '/tipos-embalagens/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = TipoEmbalagemQld.objects.last()
    assert obj.nome == 'FARDO'


def test_url_embalagen_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/tipos-embalagens/')
    assert response.status_code == status.HTTP_200_OK


def test_url_lista_nomes_tipos_embalagens_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/tipos-embalagens/lista-nomes-tipos-embalagens/')
    assert response.status_code == status.HTTP_200_OK


def test_url_lista_abreviacoes_tipos_embalagens_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/tipos-embalagens/lista-abreviacoes-tipos-embalagens/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_embalagem_update(client_autenticado_qualidade, tipo_emabalagem_qld):
    data = {
        'nome': 'saco',
        'abreviacao': 'SC'
    }
    response = client_autenticado_qualidade.put(
        f'/tipos-embalagens/{tipo_emabalagem_qld.uuid}/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_200_OK
    obj = TipoEmbalagemQld.objects.last()
    assert obj.nome == 'SACO'


def test_url_perfil_cronograma_assina_cronograma_authorized(client_autenticado_dilog_cronograma,
                                                            empresa, contrato, armazem):
    data = {
        'empresa': str(empresa.uuid),
        'password': constants.DJANGO_ADMIN_PASSWORD,
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
    response = client_autenticado_dilog_cronograma.post(
        '/cronogramas/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_url_perfil_cronograma_assina_cronograma_erro_senha(client_autenticado_dilog_cronograma,
                                                            empresa, contrato):
    data = {
        'empresa': str(empresa.uuid),
        'password': 'senha_errada',
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
    response = client_autenticado_dilog_cronograma.post(
        f'/cronogramas/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_perfil_cronograma_assina_not_authorized(client_autenticado_dilog):
    response = client_autenticado_dilog.post(
        f'/cronogramas/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_dinutre_assina_cronograma_authorized(client_autenticado_dinutre_diretoria,
                                                  cronograma_assinado_fornecedor):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_fornecedor.uuid}/dinutre-assina/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.get(uuid=cronograma_assinado_fornecedor.uuid)
    assert obj.status == 'ASSINADO_DINUTRE'


def test_url_dinutre_assina_cronograma_erro_senha(client_autenticado_dinutre_diretoria,
                                                  cronograma_assinado_fornecedor):
    data = json.dumps({'password': 'senha_errada'})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_fornecedor.uuid}/dinutre-assina/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_dinutre_assina_cronograma_erro_cronograma_invalido(client_autenticado_dinutre_diretoria):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dinutre_diretoria.patch(
        f'/cronogramas/{uuid.uuid4()}/dinutre-assina/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


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


def test_url_dilog_assina_cronograma_authorized(client_autenticado_dilog_diretoria,
                                                cronograma_assinado_perfil_dinutre):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dilog_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_perfil_dinutre.uuid}/codae-assina/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.get(uuid=cronograma_assinado_perfil_dinutre.uuid)
    assert obj.status == 'ASSINADO_CODAE'


def test_url_dilog_assina_cronograma_erro_senha(client_autenticado_dilog_diretoria,
                                                cronograma_assinado_perfil_dinutre):
    data = json.dumps({'password': 'senha_errada'})
    response = client_autenticado_dilog_diretoria.patch(
        f'/cronogramas/{cronograma_assinado_perfil_dinutre.uuid}/codae-assina/', data, content_type='application/json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_dilog_assina_cronograma_erro_cronograma_invalido(client_autenticado_dilog_diretoria):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dilog_diretoria.patch(
        f'/cronogramas/{uuid.uuid4()}/codae-assina/',
        data, content_type='application/json')
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_url_dilog_assina_cronograma_erro_transicao_estado(client_autenticado_dilog_diretoria,
                                                           cronograma):
    data = json.dumps({'password': constants.DJANGO_ADMIN_PASSWORD})
    response = client_autenticado_dilog_diretoria.patch(
        f'/cronogramas/{cronograma.uuid}/codae-assina/', data,
        content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_dilog_assina_cronograma_not_authorized(client_autenticado_dilog,
                                                    cronograma_recebido):
    response = client_autenticado_dilog.patch(
        f'/cronogramas/{cronograma_recebido.uuid}/codae-assina/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_detalhar_com_log(client_autenticado_dinutre_diretoria, cronogramas_multiplos_status_com_log):
    cronograma_com_log = Cronograma.objects.first()
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/{cronograma_com_log.uuid}/detalhar-com-log/')
    assert response.status_code == status.HTTP_200_OK


def test_url_dashboard_painel_usuario_dinutre(client_autenticado_dinutre_diretoria,
                                              cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard/'
    )
    assert response.status_code == status.HTTP_200_OK

    status_esperados = ['ASSINADO_FORNECEDOR', 'ASSINADO_DINUTRE', 'ASSINADO_CODAE']
    status_recebidos = [result['status'] for result in response.json()['results']]
    for status_esperado in status_esperados:
        assert status_esperado in status_recebidos

    resultados_recebidos = [result for result in response.json()['results']]
    for resultado in resultados_recebidos:
        if resultado['status'] == 'ASSINADO_FORNECEDOR':
            assert len(resultado['dados']) == 3
        elif resultado['status'] == 'ASSINADO_DINUTRE':
            assert len(resultado['dados']) == 2
        elif resultado['status'] == 'ASSINADO_CODAE':
            assert len(resultado['dados']) == 1


def test_url_dashboard_painel_usuario_dinutre_com_paginacao(client_autenticado_dinutre_diretoria,
                                                            cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard/?status=ASSINADO_FORNECEDOR&limit=2&offset=0'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1
    assert response.json()['results'][0]['status'] == ['ASSINADO_FORNECEDOR']
    assert response.json()['results'][0]['total'] == 3
    assert len(response.json()['results'][0]['dados']) == 2


def test_url_dashboard_com_filtro_painel_usuario_dinutre(client_autenticado_dinutre_diretoria,
                                                         cronogramas_multiplos_status_com_log):
    response = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/'
    )
    response_filtro1 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?nome_produto=Arroz'
    )
    response_filtro2 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?numero_cronograma=003/2023'
    )
    response_filtro3 = client_autenticado_dinutre_diretoria.get(
        f'/cronogramas/dashboard-com-filtro/?nome_fornecedor=Alimentos'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response_filtro1.status_code == status.HTTP_200_OK
    assert response_filtro2.status_code == status.HTTP_200_OK
    assert response_filtro3.status_code == status.HTTP_200_OK

    resultados_assinado_fornecedor = [
        r for r in response.json()['results'] if r['status'] == 'ASSINADO_FORNECEDOR'][0]
    assert len(resultados_assinado_fornecedor['dados']) == 3
    resultados_assinado_dinutre = [
        r for r in response.json()['results'] if r['status'] == 'ASSINADO_DINUTRE'][0]
    assert len(resultados_assinado_dinutre['dados']) == 2
    resultados_assinado_codae = [
        r for r in response.json()['results'] if r['status'] == 'ASSINADO_CODAE'][0]
    assert len(resultados_assinado_codae['dados']) == 1

    resultados_assinado_fornecedor = [
        r for r in response_filtro1.json()['results'] if r['status'] == 'ASSINADO_FORNECEDOR'][0]
    assert len(resultados_assinado_fornecedor['dados']) == 1
    resultados_assinado_dinutre = [
        r for r in response_filtro1.json()['results'] if r['status'] == 'ASSINADO_DINUTRE'][0]
    assert len(resultados_assinado_dinutre['dados']) == 1
    resultados_assinado_codae = [
        r for r in response_filtro1.json()['results'] if r['status'] == 'ASSINADO_CODAE'][0]
    assert len(resultados_assinado_codae['dados']) == 0

    resultados_assinado_fornecedor = [
        r for r in response_filtro2.json()['results'] if r['status'] == 'ASSINADO_FORNECEDOR'][0]
    assert len(resultados_assinado_fornecedor['dados']) == 1
    resultados_assinado_dinutre = [
        r for r in response_filtro2.json()['results'] if r['status'] == 'ASSINADO_DINUTRE'][0]
    assert len(resultados_assinado_dinutre['dados']) == 0
    resultados_assinado_codae = [
        r for r in response_filtro2.json()['results'] if r['status'] == 'ASSINADO_CODAE'][0]
    assert len(resultados_assinado_codae['dados']) == 0

    resultados_assinado_fornecedor = [
        r for r in response_filtro3.json()['results'] if r['status'] == 'ASSINADO_FORNECEDOR'][0]
    assert len(resultados_assinado_fornecedor['dados']) == 3
    resultados_assinado_dinutre = [
        r for r in response_filtro3.json()['results'] if r['status'] == 'ASSINADO_DINUTRE'][0]
    assert len(resultados_assinado_dinutre['dados']) == 2
    resultados_assinado_codae = [
        r for r in response_filtro3.json()['results'] if r['status'] == 'ASSINADO_CODAE'][0]
    assert len(resultados_assinado_codae['dados']) == 1


def test_url_dashboard_painel_solicitacao_alteracao_dinutre(client_autenticado_dinutre_diretoria,
                                                            cronogramas_multiplos_status_com_log_cronograma_ciente):
    response = client_autenticado_dinutre_diretoria.get(
        f'/solicitacao-de-alteracao-de-cronograma/dashboard/'
    )
    QTD_STATUS_DASHBOARD_DINUTRE = 5
    SOLICITACOES_STATUS_CRONOGRAMA_CIENTE = 2
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == QTD_STATUS_DASHBOARD_DINUTRE
    assert response.json()['results'][0]['status'] == 'CRONOGRAMA_CIENTE'
    assert len(response.json()['results'][0]['dados']) == SOLICITACOES_STATUS_CRONOGRAMA_CIENTE


def test_url_relatorio_cronograma_authorized(client_autenticado_dinutre_diretoria, cronograma):
    response = client_autenticado_dinutre_diretoria.get(f'/cronogramas/{str(cronograma.uuid)}/gerar-pdf-cronograma/')
    assert response.status_code == status.HTTP_200_OK


def test_url_unidades_medida_listar(client_autenticado_dilog_cronograma, unidades_medida_logistica):
    """Deve obter lista paginada de unidades de medida."""
    client = client_autenticado_dilog_cronograma

    response = client.get('/unidades-medida-logistica/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == len(unidades_medida_logistica)
    assert len(response.data['results']) == UnidadeMedidaPagination.page_size
    assert response.data['next'] is not None


def test_url_unidades_medida_listar_com_filtros(client_autenticado_dilog_cronograma, unidades_medida_reais_logistica):
    """Deve obter lista paginada e filtrada de unidades de medida."""
    client = client_autenticado_dilog_cronograma

    url_com_filtro_nome = '/unidades-medida-logistica/?nome=lit'
    response = client.get(url_com_filtro_nome)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['nome'] == 'LITRO'

    url_com_filtro_abreviacao = '/unidades-medida-logistica/?abreviacao=kg'
    response = client.get(url_com_filtro_abreviacao)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['nome'] == 'KILOGRAMA'

    data_cadastro = unidades_medida_reais_logistica[0].criado_em.date().strftime('%d/%m/%Y')
    url_com_filtro_data_cadastro = f'/unidades-medida-logistica/?data_cadastro={data_cadastro}'
    response = client.get(url_com_filtro_data_cadastro)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2

    url_com_filtro_sem_resultado = '/unidades-medida-logistica/?nome=lit&abreviacao=kg'
    response = client.get(url_com_filtro_sem_resultado)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0


def test_url_unidades_medida_detalhar(client_autenticado_dilog_cronograma, unidade_medida_logistica):
    """Deve obter detalhes de uma unidade de medida."""
    client = client_autenticado_dilog_cronograma

    response = client.get(f'/unidades-medida-logistica/{unidade_medida_logistica.uuid}/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(unidade_medida_logistica.uuid)
    assert response.data['nome'] == str(unidade_medida_logistica.nome)
    assert response.data['abreviacao'] == str(unidade_medida_logistica.abreviacao)
    assert response.data['criado_em'] == unidade_medida_logistica.criado_em.strftime(
        settings.REST_FRAMEWORK['DATETIME_FORMAT'])


def test_url_unidades_medida_criar(client_autenticado_dilog_cronograma):
    """Deve criar com sucesso uma unidade de medida."""
    client = client_autenticado_dilog_cronograma
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE',
        'abreviacao': 'umt'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['nome'] == payload['nome']
    assert response.data['abreviacao'] == payload['abreviacao']
    assert UnidadeMedida.objects.filter(uuid=response.data['uuid']).exists()


def test_url_unidades_medida_criar_com_nome_invalido(client_autenticado_dilog_cronograma):
    """Deve falhar ao tentar criar uma unidade de medida com atributo nome inválido (caixa baixa)."""
    client = client_autenticado_dilog_cronograma
    payload = {
        'nome': 'unidade medida teste',
        'abreviacao': 'umt'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data['nome'][0]) == 'O campo deve conter apenas letras maiúsculas.'


def test_url_unidades_medida_criar_com_abreviacao_invalida(client_autenticado_dilog_cronograma):
    """Deve falhar ao tentar criar uma unidade de medida com atributo abreviacao inválida (caixa alta)."""
    client = client_autenticado_dilog_cronograma
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE',
        'abreviacao': 'UMT'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data['abreviacao'][0]) == 'O campo deve conter apenas letras minúsculas.'


def test_url_unidades_medida_criar_repetida(client_autenticado_dilog_cronograma, unidade_medida_logistica):
    """Deve falhar ao tentar criar uma unidade de medida que já esteja cadastrada."""
    client = client_autenticado_dilog_cronograma
    payload = {
        'nome': 'UNIDADE TESTE',
        'abreviacao': 'ut'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'][0].code == 'unique'


def test_url_unidades_medida_atualizar(client_autenticado_dilog_cronograma, unidade_medida_logistica):
    """Deve atualizar com sucesso uma unidade de medida."""
    client = client_autenticado_dilog_cronograma
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE ATUALIZADA',
        'abreviacao': 'umta'
    }

    response = client.patch(f'/unidades-medida-logistica/{unidade_medida_logistica.uuid}/', data=json.dumps(payload),
                            content_type='application/json')

    unidade_medida_logistica.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == unidade_medida_logistica.nome == payload['nome']
    assert response.data['abreviacao'] == unidade_medida_logistica.abreviacao == payload['abreviacao']


def test_url_unidades_medida_action_listar_nomes_abreviacoes(client_autenticado_dilog_cronograma,
                                                             unidades_medida_logistica):
    """Deve obter lista com nomes e abreviações de todas as unidades de medida cadastradas."""
    client = client_autenticado_dilog_cronograma
    response = client.get('/unidades-medida-logistica/lista-nomes-abreviacoes/')

    unidades_medida = UnidadeMedida.objects.all().order_by('-criado_em')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == len(unidades_medida_logistica)
    assert response.data['results'] == NomeEAbreviacaoUnidadeMedidaSerializer(unidades_medida, many=True).data


def test_url_cronograma_action_listar_para_cadastro_de_layout(client_autenticado_fornecedor):
    """Deve obter lista com numeros, pregao e nome do produto de todas os produtos cadastradas."""
    client = client_autenticado_fornecedor
    response = client.get('/cronogramas/lista-cronogramas-cadastro-layout/')

    cronogramas = Cronograma.objects.all().order_by('-criado_em')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == CronogramaSimplesSerializer(cronogramas, many=True).data


def test_url_endpoint_layout_de_embalagem_create(client_autenticado_fornecedor,
                                                 cronograma_assinado_perfil_dilog, arquivo_base64):
    data = {
        'cronograma': str(cronograma_assinado_perfil_dilog.uuid),
        'observacoes': 'Imagine uma observação aqui.',
        'tipos_de_embalagens': [
            {
                'tipo_embalagem': 'PRIMARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    },
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo2.jpg'
                    }
                ]
            },
            {
                'tipo_embalagem': 'SECUNDARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    }
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.post(
        '/layouts-de-embalagem/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_201_CREATED
    obj = LayoutDeEmbalagem.objects.last()
    assert obj.status == LayoutDeEmbalagem.workflow_class.ENVIADO_PARA_ANALISE
    assert obj.tipos_de_embalagens.count() == 2


def test_url_endpoint_layout_de_embalagem_create_cronograma_nao_existe(client_autenticado_fornecedor):
    """Uuid do cronograma precisa existir na base, imagens_do_tipo_de_embalagem e arquivo são obrigatórios."""
    data = {
        'cronograma': str(uuid.uuid4()),
        'observacoes': 'Imagine uma observação aqui.',
        'tipos_de_embalagens': [
            {
                'tipo_embalagem': 'PRIMARIA',
            },
            {
                'tipo_embalagem': 'SECUNDARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': '',
                        'nome': 'Anexo1.jpg'
                    }
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.post(
        '/layouts-de-embalagem/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Cronograma não existe' in response.data['cronograma']
    assert 'Este campo é obrigatório.' in response.data['tipos_de_embalagens'][0]['imagens_do_tipo_de_embalagem']


def test_url_layout_de_embalagem_listagem(client_autenticado_qualidade, lista_layouts_de_embalagem):
    """Deve obter lista paginada de layouts de embalagens."""
    client = client_autenticado_qualidade
    response = client.get('/layouts-de-embalagem/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == len(lista_layouts_de_embalagem)
    assert len(response.data['results']) == LayoutDeEmbalagemPagination.page_size
    assert response.data['next'] is not None


def test_url_dashboard_layout_embalagens(client_autenticado_codae_dilog, lista_layouts_de_embalagem):
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/')

    assert response.status_code == status.HTTP_200_OK

    status_esperados = [LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE]
    status_recebidos = [result['status'] for result in response.json()['results']]
    for status_esperado in status_esperados:
        assert status_esperado in status_recebidos

    assert len(response.json()['results'][0]['dados']) == 5


def test_url_dashboard_layout_embalagens_com_filtro(client_autenticado_codae_dilog, lista_layouts_de_embalagem):
    filtros = {'numero_cronograma': '003/2022'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results'][0]['dados']) == 4

    filtros = {'nome_produto': 'Arroz'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results'][0]['dados']) == 4

    filtros = {'numero_cronograma': '004/2022'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results'][0]['dados']) == 5

    filtros = {'nome_produto': 'Macarrão'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results'][0]['dados']) == 5

    filtros = {'nome_fornecedor': 'Alimentos'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results'][0]['dados']) == 5


def test_url_dashboard_layout_embalagens_ver_mais(
    client_autenticado_codae_dilog, lista_layouts_de_embalagem_enviados_para_analise
):
    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']['dados']) == 10
    assert response.json()['results']['total'] == len(lista_layouts_de_embalagem_enviados_para_analise)


def test_url_dashboard_layout_embalagens_ver_mais_com_filtros(
    client_autenticado_codae_dilog, lista_layouts_de_embalagem_enviados_para_analise
):
    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10,
        'numero_cronograma': '003/2022',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 4

    layouts_esperados = LayoutDeEmbalagem.objects.filter(cronograma__numero='003/2022').order_by('-criado_em')[:10]
    primeiro_layout_esperado = layouts_esperados[0]
    ultimo_layout_esperado = layouts_esperados[3]
    assert str(primeiro_layout_esperado.uuid) == response.json()['results']['dados'][0]['uuid']
    assert str(ultimo_layout_esperado.uuid) == response.json()['results']['dados'][-1]['uuid']

    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10,
        'nome_produto': 'Arroz',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 4

    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10,
        'numero_cronograma': '004/2022',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10

    layouts_esperados = LayoutDeEmbalagem.objects.filter(cronograma__numero='004/2022').order_by('-criado_em')[:10]
    primeiro_layout_esperado = layouts_esperados[0]
    ultimo_layout_esperado = layouts_esperados[9]
    assert str(primeiro_layout_esperado.uuid) == response.json()['results']['dados'][0]['uuid']
    assert str(ultimo_layout_esperado.uuid) == response.json()['results']['dados'][-1]['uuid']

    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10,
        'nome_produto': 'Macarrão',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10

    filtros = {
        'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        'offset': 0,
        'limit': 10,
        'nome_fornecedor': 'Alimentos',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10
