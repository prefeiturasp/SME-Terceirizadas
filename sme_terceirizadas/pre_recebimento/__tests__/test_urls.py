import datetime
import json
import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from sme_terceirizadas.dados_comuns import constants
from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.fluxo_status import DocumentoDeRecebimentoWorkflow, LayoutDeEmbalagemWorkflow
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import (
    CronogramaSimplesSerializer,
    NomeEAbreviacaoUnidadeMedidaSerializer
)
from sme_terceirizadas.pre_recebimento.api.services import (
    ServiceDashboardDocumentosDeRecebimento,
    ServiceDashboardLayoutEmbalagem
)
from sme_terceirizadas.pre_recebimento.fixtures.factories.documentos_de_recebimento_factory import fake
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    DocumentoDeRecebimento,
    Laboratorio,
    LayoutDeEmbalagem,
    SolicitacaoAlteracaoCronograma,
    TipoDeDocumentoDeRecebimento,
    TipoEmbalagemQld,
    UnidadeMedida
)


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
    assert len(response.data['results']) == DefaultPagination.page_size
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


def test_url_cronograma_action_listar_para_cadastro(client_autenticado_fornecedor,
                                                    django_user_model, cronograma_factory):
    """Deve obter lista com numeros, pregao e nome do produto dos cronogramas cadastrados do fornecedor."""
    user_id = client_autenticado_fornecedor.session['_auth_user_id']
    empresa = django_user_model.objects.get(pk=user_id).vinculo_atual.instituicao
    cronogramas_do_fornecedor = [cronograma_factory.create(empresa=empresa) for _ in range(10)]
    outros_cronogramas = [cronograma_factory.create() for _ in range(5)]
    todos_cronogramas = cronogramas_do_fornecedor + outros_cronogramas
    response = client_autenticado_fornecedor.get('/cronogramas/lista-cronogramas-cadastro/')

    cronogramas = Cronograma.objects.filter(empresa=empresa).order_by('-criado_em')

    # Testa se o usuário fornecedor acessa apenas os seus cronogramas
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == CronogramaSimplesSerializer(cronogramas, many=True).data
    assert len(response.data['results']) == len(cronogramas_do_fornecedor)

    # Testa se a quantidade de cronogramas do response é diferente da quantidade total de cronogramas
    assert len(response.data['results']) != len(todos_cronogramas)


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
    assert len(response.data['results']) == DefaultPagination.page_size
    assert response.data['next'] is not None


def test_url_layout_de_embalagem_detalhar(client_autenticado_codae_dilog, lista_layouts_de_embalagem):
    layout_esperado = LayoutDeEmbalagem.objects.first()
    cronograma_esperado = layout_esperado.cronograma

    response = client_autenticado_codae_dilog.get(f'/layouts-de-embalagem/{layout_esperado.uuid}/')
    dedos_layout_recebido = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert dedos_layout_recebido['uuid'] == str(layout_esperado.uuid)
    assert dedos_layout_recebido['observacoes'] == str(layout_esperado.observacoes)
    assert dedos_layout_recebido['criado_em'] == layout_esperado.criado_em.strftime(
        settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    assert dedos_layout_recebido['status'] == layout_esperado.get_status_display()
    assert dedos_layout_recebido['numero_cronograma'] == str(cronograma_esperado.numero)
    assert dedos_layout_recebido['pregao_chamada_publica'] == str(cronograma_esperado.contrato.pregao_chamada_publica)
    assert dedos_layout_recebido['nome_produto'] == str(cronograma_esperado.produto.nome)
    assert dedos_layout_recebido['nome_empresa'] == str(cronograma_esperado.empresa.razao_social)


def test_url_dashboard_layout_embalagens_status_retornados(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem
):
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/')

    assert response.status_code == status.HTTP_200_OK

    user = get_user_model().objects.get()
    status_esperados = ServiceDashboardLayoutEmbalagem.get_dashboard_status(user)
    status_recebidos = [result['status'] for result in response.json()['results']]

    for status_recebido in status_recebidos:
        assert status_recebido in status_esperados


@pytest.mark.parametrize(
    'status_card',
    [
        LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        LayoutDeEmbalagemWorkflow.APROVADO,
        LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
    ]
)
def test_url_dashboard_layout_embalagens_quantidade_itens_por_card(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem,
    status_card
):
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/')

    assert response.status_code == status.HTTP_200_OK

    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']

    assert len(dados_card) == 6


@pytest.mark.parametrize(
    'status_card',
    [
        LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        LayoutDeEmbalagemWorkflow.APROVADO,
        LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
    ]
)
def test_url_dashboard_layout_embalagens_com_filtro(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem,
    status_card
):
    filtros = {'numero_cronograma': '003/2022'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']
    assert len(dados_card) == 5

    filtros = {'nome_produto': 'Arroz'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']
    assert len(dados_card) == 5

    filtros = {'numero_cronograma': '004/2022'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']
    assert len(dados_card) == 6

    filtros = {'nome_produto': 'Macarrão'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']
    assert len(dados_card) == 6

    filtros = {'nome_fornecedor': 'Alimentos'}
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']
    assert len(dados_card) == 6


@pytest.mark.parametrize(
    'status_card',
    [
        LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        LayoutDeEmbalagemWorkflow.APROVADO,
        LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
    ]
)
def test_url_dashboard_layout_embalagens_ver_mais(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem,
    status_card
):
    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']['dados']) == 10

    total_cards_esperado = LayoutDeEmbalagem.objects.filter(status=status_card).count()
    assert response.json()['results']['total'] == total_cards_esperado


@pytest.mark.parametrize(
    'status_card',
    [
        LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
        LayoutDeEmbalagemWorkflow.APROVADO,
        LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
    ]
)
def test_url_dashboard_layout_embalagens_ver_mais_com_filtros(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem,
    status_card
):
    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'numero_cronograma': '003/2022',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 5

    layouts_esperados = LayoutDeEmbalagem.objects.filter(
        status=status_card,
        cronograma__numero='003/2022'
    ).order_by('-criado_em')[:10]
    primeiro_layout_esperado = layouts_esperados[0]
    ultimo_layout_esperado = layouts_esperados[4]
    assert str(primeiro_layout_esperado.uuid) == response.json()['results']['dados'][0]['uuid']
    assert str(ultimo_layout_esperado.uuid) == response.json()['results']['dados'][-1]['uuid']

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'nome_produto': 'Arroz',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 5

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'numero_cronograma': '004/2022',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10

    layouts_esperados = LayoutDeEmbalagem.objects.filter(
        status=status_card,
        cronograma__numero='004/2022'
    ).order_by('-criado_em')[:10]
    primeiro_layout_esperado = layouts_esperados[0]
    ultimo_layout_esperado = layouts_esperados[9]
    assert str(primeiro_layout_esperado.uuid) == response.json()['results']['dados'][0]['uuid']
    assert str(ultimo_layout_esperado.uuid) == response.json()['results']['dados'][-1]['uuid']

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'nome_produto': 'Macarrão',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'nome_fornecedor': 'Alimentos',
    }
    response = client_autenticado_codae_dilog.get('/layouts-de-embalagem/dashboard/', filtros)
    assert len(response.json()['results']['dados']) == 10


def test_url_layout_embalagens_analise_aprovando(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem_com_tipo_embalagem
):
    layout_analisado = lista_layouts_de_embalagem_com_tipo_embalagem[0]
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='TERCIARIA').uuid),
                'tipo_embalagem': 'TERCIARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )
    layout_analisado.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert layout_analisado.aprovado

    layout_analisado = lista_layouts_de_embalagem_com_tipo_embalagem[1]
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )
    layout_analisado.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert layout_analisado.aprovado


def test_url_layout_embalagens_analise_solicitando_correcao(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem_com_tipo_embalagem
):
    layout_analisado = lista_layouts_de_embalagem_com_tipo_embalagem[0]
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='TERCIARIA').uuid),
                'tipo_embalagem': 'TERCIARIA',
                'status': 'REPROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )
    layout_analisado.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert not layout_analisado.aprovado

    layout_analisado = lista_layouts_de_embalagem_com_tipo_embalagem[1]
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'REPROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )
    layout_analisado.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert not layout_analisado.aprovado


def test_url_layout_embalagens_validacao_primeira_analise(
    client_autenticado_codae_dilog,
    lista_layouts_de_embalagem_com_tipo_embalagem
):
    layout_analisado = lista_layouts_de_embalagem_com_tipo_embalagem[0]
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )

    msg_erro = (
        'Quantidade de Tipos de Embalagem recebida para primeira análise ' +
        'é diferente da quantidade presente no Layout de Embalagem.'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro in response.json()['tipos_de_embalagens']


def test_url_layout_embalagens_analise_correcao(
    client_autenticado_codae_dilog,
    layout_de_embalagem_em_analise_com_correcao
):
    layout_analisado = layout_de_embalagem_em_analise_com_correcao
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='TERCIARIA').uuid),
                'tipo_embalagem': 'TERCIARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    assert not layout_analisado.eh_primeira_analise

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )
    layout_analisado.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert layout_analisado.aprovado


def test_url_layout_embalagens_validacao_analise_correcao(
    client_autenticado_codae_dilog,
    layout_de_embalagem_em_analise_com_correcao
):
    layout_analisado = layout_de_embalagem_em_analise_com_correcao
    tipos_embalagem_analisados = layout_analisado.tipos_de_embalagens.all()
    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'status': 'REPROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    assert not layout_analisado.eh_primeira_analise

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )

    msg_erro = 'O Tipo/UUID informado não pode ser analisado pois não está em análise.'
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro in response.json()['tipos_de_embalagens'][1]['Layout Embalagem SECUNDARIA']

    dados_analise = {
        'tipos_de_embalagens': [
            {
                'uuid': str(tipos_embalagem_analisados.get(tipo_embalagem='PRIMARIA').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'status': 'APROVADO',
                'complemento_do_status': 'Teste complemento',
            },
        ],
    }

    response = client_autenticado_codae_dilog.patch(
        f'/layouts-de-embalagem/{layout_analisado.uuid}/codae-aprova-ou-solicita-correcao/',
        content_type='application/json',
        data=json.dumps(dados_analise)
    )

    msg_erro = (
        'Quantidade de Tipos de Embalagem recebida para análise da correção ' +
        'é diferente da quantidade em análise.'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro in response.json()['tipos_de_embalagens']


def test_url_endpoint_layout_de_embalagem_fornecedor_corrige(client_autenticado_fornecedor, arquivo_base64,
                                                             layout_de_embalagem_para_correcao):
    layout_para_corrigir = layout_de_embalagem_para_correcao
    dados_correcao = {
        'observacoes': 'Imagine uma nova observação aqui.',
        'tipos_de_embalagens': [
            {
                'uuid': str(layout_para_corrigir.tipos_de_embalagens.get(status='REPROVADO').uuid),
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
        ],
    }

    response = client_autenticado_fornecedor.patch(
        f'/layouts-de-embalagem/{layout_para_corrigir.uuid}/fornecedor-realiza-correcao/',
        content_type='application/json',
        data=json.dumps(dados_correcao)
    )

    layout_para_corrigir.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert layout_para_corrigir.status == LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
    assert layout_para_corrigir.observacoes == 'Imagine uma nova observação aqui.'


def test_url_endpoint_layout_de_embalagem_fornecedor_corrige_not_ok(client_autenticado_fornecedor, arquivo_base64,
                                                                    layout_de_embalagem_para_correcao):
    """Checa transição de estado, UUID valido de tipo de embalagem e se pode ser de fato corrigido."""
    layout_para_corrigir = layout_de_embalagem_para_correcao
    dados = {
        'observacoes': 'Imagine uma nova observação aqui.',
        'tipos_de_embalagens': [
            {
                'uuid': str(uuid.uuid4()),
                'tipo_embalagem': 'SECUNDARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    },
                ]
            },
            {
                'uuid': str(layout_para_corrigir.tipos_de_embalagens.get(status='APROVADO').uuid),
                'tipo_embalagem': 'TERCIARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    },
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.patch(
        f'/layouts-de-embalagem/{layout_para_corrigir.uuid}/fornecedor-realiza-correcao/',
        content_type='application/json',
        data=json.dumps(dados)
    )

    msg_erro1 = 'UUID do tipo informado não existe.'
    msg_erro2 = 'O Tipo/UUID informado não pode ser corrigido pois não está reprovado.'
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro1 in response.json()['tipos_de_embalagens'][0]['Layout Embalagem SECUNDARIA'][0]
    assert msg_erro2 in response.json()['tipos_de_embalagens'][1]['Layout Embalagem TERCIARIA'][0]

    dados = {
        'observacoes': 'Imagine uma nova observação aqui.',
        'tipos_de_embalagens': [
            {
                'uuid': str(layout_para_corrigir.tipos_de_embalagens.get(status='REPROVADO').uuid),
                'tipo_embalagem': 'PRIMARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    },
                ]
            },
        ],
    }

    layout_para_corrigir.status = LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
    layout_para_corrigir.save()

    response = client_autenticado_fornecedor.patch(
        f'/layouts-de-embalagem/{layout_para_corrigir.uuid}/fornecedor-realiza-correcao/',
        content_type='application/json',
        data=json.dumps(dados)
    )

    msg_erro3 = 'Erro de transição de estado. O status deste layout não permite correção'
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro3 in response.json()[0]


def test_url_endpoint_layout_de_embalagem_fornecedor_atualiza(client_autenticado_fornecedor, arquivo_base64,
                                                              layout_de_embalagem_aprovado):
    layout_para_atualizar = layout_de_embalagem_aprovado
    dados_correcao = {
        'observacoes': 'Imagine uma nova observação aqui.',
        'tipos_de_embalagens': [
            {
                'uuid': str(layout_para_atualizar.tipos_de_embalagens.get(tipo_embalagem='PRIMARIA').uuid),
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
                'uuid': str(layout_para_atualizar.tipos_de_embalagens.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo3.jpg'
                    },
                ]
            },
            {
                'tipo_embalagem': 'TERCIARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo4.jpg'
                    },
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.patch(
        f'/layouts-de-embalagem/{layout_para_atualizar.uuid}/',
        content_type='application/json',
        data=json.dumps(dados_correcao)
    )

    layout_para_atualizar.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert layout_para_atualizar.status == LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
    assert layout_para_atualizar.observacoes == 'Imagine uma nova observação aqui.'


def test_url_endpoint_layout_de_embalagem_fornecedor_atualiza_not_ok(client_autenticado_fornecedor, arquivo_base64,
                                                                     layout_de_embalagem_para_correcao):
    """Checa transição de estado."""
    layout_para_atualizar = layout_de_embalagem_para_correcao

    dados = {
        'observacoes': 'Imagine uma nova observação aqui.',
        'tipos_de_embalagens': [
            {
                'uuid': str(layout_para_atualizar.tipos_de_embalagens.get(tipo_embalagem='SECUNDARIA').uuid),
                'tipo_embalagem': 'SECUNDARIA',
                'imagens_do_tipo_de_embalagem': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    },
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.patch(
        f'/layouts-de-embalagem/{layout_para_atualizar.uuid}/',
        content_type='application/json',
        data=json.dumps(dados)
    )

    msg_erro3 = 'Erro de transição de estado. O status deste layout não permite correção'
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert msg_erro3 in response.json()[0]


def test_url_endpoint_documentos_recebimento_create(client_autenticado_fornecedor,
                                                    cronograma_factory, arquivo_base64):
    cronograma_obj = cronograma_factory.create()
    data = {
        'cronograma': str(cronograma_obj.uuid),
        'numero_laudo': '123456789',
        'tipos_de_documentos': [
            {
                'tipo_documento': TipoDeDocumentoDeRecebimento.TIPO_DOC_LAUDO,
                'arquivos_do_tipo_de_documento': [
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
                'tipo_documento': TipoDeDocumentoDeRecebimento.TIPO_DOC_RASTREABILIDADE,
                'arquivos_do_tipo_de_documento': [
                    {
                        'arquivo': arquivo_base64,
                        'nome': 'Anexo1.jpg'
                    }
                ]
            },
        ],
    }

    response = client_autenticado_fornecedor.post(
        '/documentos-de-recebimento/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_201_CREATED
    obj = DocumentoDeRecebimento.objects.last()
    assert obj.status == DocumentoDeRecebimento.workflow_class.ENVIADO_PARA_ANALISE
    assert obj.tipos_de_documentos.count() == 2

    # Teste de cadastro quando o cronograma informado não existe ou quando o arquivo não é enviado
    data['cronograma'] = fake.uuid4()
    data['tipos_de_documentos'][1].pop('arquivos_do_tipo_de_documento')

    response = client_autenticado_fornecedor.post(
        '/documentos-de-recebimento/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Cronograma não existe' in response.data['cronograma']
    assert 'Este campo é obrigatório.' in response.data['tipos_de_documentos'][1]['arquivos_do_tipo_de_documento']


def test_url_documentos_de_recebimento_listagem(client_autenticado_fornecedor, django_user_model,
                                                documento_de_recebimento_factory):
    """Deve obter lista paginada e filtrada de documentos de recebimento."""
    user_id = client_autenticado_fornecedor.session['_auth_user_id']
    empresa = django_user_model.objects.get(pk=user_id).vinculo_atual.instituicao
    documentos = [documento_de_recebimento_factory.create(cronograma__empresa=empresa) for _ in range(11)]
    response = client_autenticado_fornecedor.get('/documentos-de-recebimento/')

    assert response.status_code == status.HTTP_200_OK

    # Teste de paginação
    assert response.data['count'] == len(documentos)
    assert len(response.data['results']) == DefaultPagination.page_size
    assert response.data['next'] is not None

    # Acessa a próxima página
    next_page = response.data['next']
    next_response = client_autenticado_fornecedor.get(next_page)
    assert next_response.status_code == status.HTTP_200_OK

    # Tenta acessar uma página que não existe
    response_not_found = client_autenticado_fornecedor.get('/documentos-de-recebimento/?page=1000')
    assert response_not_found.status_code == status.HTTP_404_NOT_FOUND

    # Testa a resposta em caso de erro (por exemplo, sem autenticação)
    client_nao_autenticado = APIClient()
    response_error = client_nao_autenticado.get('/documentos-de-recebimento/')
    assert response_error.status_code == status.HTTP_401_UNAUTHORIZED

    # Teste de consulta com parâmetros
    data = datetime.date.today() - datetime.timedelta(days=1)
    response_filtro = client_autenticado_fornecedor.get(f'/documentos-de-recebimento/?data_cadastro={data}')
    assert response_filtro.status_code == status.HTTP_200_OK
    assert response_filtro.data['count'] == 0


def test_url_documentos_de_recebimento_listagem_not_authorized(client_autenticado):
    """Teste de requisição quando usuário não tem permissão."""
    response = client_autenticado.get('/documentos-de-recebimento/')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_dashboard_documentos_de_recebimento_status_retornados(
    client_autenticado_codae_dilog,
    documento_de_recebimento_factory
):
    user = get_user_model().objects.get()
    status_esperados = ServiceDashboardDocumentosDeRecebimento.get_dashboard_status(user)
    for status_esperado in status_esperados:
        documento_de_recebimento_factory(status=status_esperado)

    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/')

    assert response.status_code == status.HTTP_200_OK

    status_recebidos = [result['status'] for result in response.json()['results']]

    for status_recebido in status_recebidos:
        assert status_recebido in status_esperados


@pytest.mark.parametrize(
    'status_card',
    [
        DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
        DocumentoDeRecebimentoWorkflow.APROVADO,
    ],
)
def test_url_dashboard_documentos_de_recebimento_quantidade_itens_por_card(
    client_autenticado_codae_dilog,
    documento_de_recebimento_factory,
    status_card
):
    documento_de_recebimento_factory.create_batch(size=10, status=status_card)

    response = client_autenticado_codae_dilog.get(
        '/documentos-de-recebimento/dashboard/'
    )

    assert response.status_code == status.HTTP_200_OK

    dados_card = list(
        filter(lambda e: e['status'] == status_card, response.json()['results'])
    ).pop()['dados']

    assert len(dados_card) == 6


@pytest.mark.parametrize(
    'status_card',
    [
        DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
        DocumentoDeRecebimentoWorkflow.APROVADO,
    ]
)
def test_url_dashboard_documentos_de_recebimento_com_filtro(
    client_autenticado_codae_dilog,
    documento_de_recebimento_factory,
    status_card
):
    documentos_de_recebimento = documento_de_recebimento_factory.create_batch(size=10, status=status_card)

    filtros = {'numero_cronograma': documentos_de_recebimento[0].cronograma.numero}
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']

    assert len(dados_card) == 1

    filtros = {'nome_produto': documentos_de_recebimento[0].cronograma.produto.nome}
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']

    assert len(dados_card) == 1

    filtros = {'nome_fornecedor': documentos_de_recebimento[0].cronograma.empresa.razao_social}
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)
    dados_card = list(filter(
        lambda e: e['status'] == status_card,
        response.json()['results']
    )).pop()['dados']

    assert len(dados_card) == 1


@pytest.mark.parametrize(
    'status_card',
    [
        DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
        DocumentoDeRecebimentoWorkflow.APROVADO,
    ]
)
def test_url_dashboard_documentos_de_recebimento_ver_mais(
    client_autenticado_codae_dilog,
    documento_de_recebimento_factory,
    status_card
):
    documentos_de_recebimento = documento_de_recebimento_factory.create_batch(size=10, status=status_card)

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10
    }
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']['dados']) == 10

    assert response.json()['results']['total'] == len(documentos_de_recebimento)


@pytest.mark.parametrize(
    'status_card',
    [
        DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
        DocumentoDeRecebimentoWorkflow.APROVADO,
    ]
)
def test_url_dashboard_documentos_de_recebimento_ver_mais_com_filtros(
    client_autenticado_codae_dilog,
    documento_de_recebimento_factory,
    status_card
):
    documentos_de_recebimento = documento_de_recebimento_factory.create_batch(size=10, status=status_card)

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'numero_cronograma': documentos_de_recebimento[0].cronograma.numero
    }
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)

    assert len(response.json()['results']['dados']) == 1

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'nome_produto': documentos_de_recebimento[0].cronograma.produto.nome
    }
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)

    assert len(response.json()['results']['dados']) == 1

    filtros = {
        'status': status_card,
        'offset': 0,
        'limit': 10,
        'nome_fornecedor': documentos_de_recebimento[0].cronograma.empresa.razao_social
    }
    response = client_autenticado_codae_dilog.get('/documentos-de-recebimento/dashboard/', filtros)

    assert len(response.json()['results']['dados']) == 1


def test_url_documentos_de_recebimento_detalhar(client_autenticado_fornecedor, documento_de_recebimento_factory,
                                                cronograma_factory, django_user_model,
                                                tipo_de_documento_de_recebimento_factory):
    user_id = client_autenticado_fornecedor.session['_auth_user_id']
    empresa = django_user_model.objects.get(pk=user_id).vinculo_atual.instituicao
    contrato = empresa.contratos.first()
    cronograma = cronograma_factory.create(empresa=empresa, contrato=contrato)
    documento_de_recebimento = documento_de_recebimento_factory.create(cronograma=cronograma)
    tipo_de_documento_de_recebimento_factory.create(documento_recebimento=documento_de_recebimento)

    response = client_autenticado_fornecedor.get(f'/documentos-de-recebimento/{documento_de_recebimento.uuid}/')
    dedos_documento_de_recebimento = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert dedos_documento_de_recebimento['uuid'] == str(documento_de_recebimento.uuid)
    assert dedos_documento_de_recebimento['numero_laudo'] == str(documento_de_recebimento.numero_laudo)
    assert dedos_documento_de_recebimento['criado_em'] == documento_de_recebimento.criado_em.strftime('%d/%m/%Y')
    assert dedos_documento_de_recebimento['status'] == documento_de_recebimento.get_status_display()
    assert dedos_documento_de_recebimento['numero_cronograma'] == str(cronograma.numero)
    assert dedos_documento_de_recebimento['nome_produto'] == str(cronograma.produto.nome)
    assert dedos_documento_de_recebimento['pregao_chamada_publica'] == str(cronograma.contrato.pregao_chamada_publica)
    assert dedos_documento_de_recebimento['tipos_de_documentos'] is not None
    assert dedos_documento_de_recebimento['tipos_de_documentos'][0]['tipo_documento'] == 'LAUDO'


def test_url_documentos_de_recebimento_analisar_documento(documento_de_recebimento_factory, laboratorio_factory,
                                                          unidade_medida_factory, client_autenticado_qualidade):
    """Testa o cenário de rascunho, aprovação e sol. de correção."""
    documento = documento_de_recebimento_factory.create(
        status=DocumentoDeRecebimento.workflow_class.ENVIADO_PARA_ANALISE)
    laboratorio = laboratorio_factory.create(credenciado=True)
    unidade_medida = unidade_medida_factory()

    # Teste salvar rascunho (todos os campos não são obrigatórios)
    dados_atualizados = {
        'laboratorio': str(laboratorio.uuid),
        'quantidade_laudo': 10.5,
        'unidade_medida': str(unidade_medida.uuid),
        'data_fabricacao_lote': str(datetime.date.today()),
        'validade_produto': str(datetime.date.today()),
        'data_final_lote': str(datetime.date.today()),
        'saldo_laudo': 5.5
    }

    response_rascunho = client_autenticado_qualidade.patch(
        f'/documentos-de-recebimento/{documento.uuid}/analise-documentos-rascunho/',
        content_type='application/json',
        data=json.dumps(dados_atualizados)
    )

    documento.refresh_from_db()
    assert response_rascunho.status_code == status.HTTP_200_OK
    assert documento.status == DocumentoDeRecebimento.workflow_class.ENVIADO_PARA_ANALISE
    assert documento.laboratorio == laboratorio
    assert documento.quantidade_laudo == 10.5
    assert documento.unidade_medida == unidade_medida
    assert documento.data_fabricacao_lote == datetime.date.today()
    assert documento.validade_produto == datetime.date.today()
    assert documento.data_final_lote == datetime.date.today()
    assert documento.saldo_laudo == 5.5

    # Teste analise ação aprovar (Todos os campos são obrigatórios)
    dados_atualizados['quantidade_laudo'] = 20
    dados_atualizados['datas_fabricacao_e_prazos'] = [
        {
            'data_fabricacao': str(datetime.date.today()),
            'prazo_maximo_recebimento': '30'
        },
        {
            'data_fabricacao': str(datetime.date.today()),
            'prazo_maximo_recebimento': '60'
        },
        {
            'data_fabricacao': str(datetime.date.today()),
            'prazo_maximo_recebimento': '30'
        }
    ]

    response_aprovado = client_autenticado_qualidade.patch(
        f'/documentos-de-recebimento/{documento.uuid}/analise-documentos/',
        content_type='application/json',
        data=json.dumps(dados_atualizados)
    )

    documento.refresh_from_db()
    assert response_aprovado.status_code == status.HTTP_200_OK
    assert documento.status == DocumentoDeRecebimento.workflow_class.APROVADO
    assert documento.quantidade_laudo == 20
    assert documento.datas_fabricacao_e_prazos.count() == 3

    # Teste analise ação solicitar correção (Todos os campos são obrigatórios + correcao_solicitada)
    dados_atualizados['correcao_solicitada'] = 'Documentos corrompidos, sem possibilidade de análise.'
    documento.status = DocumentoDeRecebimento.workflow_class.ENVIADO_PARA_ANALISE
    documento.save()

    response_correcao = client_autenticado_qualidade.patch(
        f'/documentos-de-recebimento/{documento.uuid}/analise-documentos/',
        content_type='application/json',
        data=json.dumps(dados_atualizados)
    )

    documento.refresh_from_db()
    assert response_correcao.status_code == status.HTTP_200_OK
    assert documento.status == DocumentoDeRecebimento.workflow_class.ENVIADO_PARA_CORRECAO
    assert documento.correcao_solicitada == 'Documentos corrompidos, sem possibilidade de análise.'
