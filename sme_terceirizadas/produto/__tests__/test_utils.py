from datetime import date, datetime

import pytest
from model_mommy import mommy

from ..utils import (
    changes_between,
    compara_lista_protocolos,
    converte_para_datetime,
    cria_filtro_aditivos,
    cria_filtro_produto_por_parametros_form,
    get_filtros_data_em_analise_sensorial
)

pytestmark = pytest.mark.django_db


def test_cria_filtro_produto_por_parametros_form_vazio():
    campos_filtrados = cria_filtro_produto_por_parametros_form({})
    assert campos_filtrados == {}


def test_cria_filtro_produto_por_parametros_form_parametros():
    parametros = {
        'nome_fabricante': 'fabricante__nome__icontains',
        'nome_marca': 'marca__nome__icontains',
        'nome_produto': 'nome__icontains',
        'nome_terceirizada': 'homologacoes__rastro_terceirizada__nome_fantasia__icontains',
        'data_inicial': 'homologacoes__criado_em__gte',
        'status': 'homologacoes__status__in',
        'tem_aditivos_alergenicos': 'tem_aditivos_alergenicos',
        'eh_para_alunos_com_dieta': 'eh_para_alunos_com_dieta'
    }
    VALOR = 'qualquer coisa'
    for parametro_form, parametro_filtro in parametros.items():
        form_data = {
            parametro_form: VALOR
        }
        campos_filtrados = cria_filtro_produto_por_parametros_form(form_data)
        assert campos_filtrados[parametro_filtro] == VALOR


def test_cria_filtro_produto_por_parametros_form_data_final():
    data = date(2020, 4, 30)
    campos_filtrados = cria_filtro_produto_por_parametros_form({
        'data_final': data
    })
    assert campos_filtrados['homologacoes__criado_em__lt'] == date(2020, 5, 1)


def test_get_filtros_data_em_analise_sensorial_sem_data_final():
    data_analise_incial = date(2020, 8, 13)
    filtros_data = get_filtros_data_em_analise_sensorial(data_analise_incial, None)
    assert filtros_data['criado_em__gte'] == date(2020, 8, 13)


def test_converte_para_datetime():
    data_str = '13/08/2020'
    data_datetime = converte_para_datetime(data_str)
    data_datetime_aux = datetime.strptime(data_str, '%d/%m/%Y')
    assert data_datetime == data_datetime_aux


def test_cria_filtro_aditivos():
    filtro = cria_filtro_aditivos('aditivo01, aditivo02')
    assert len(filtro) == 2


def test_compara_lista_protocolos(protocolo1, protocolo2, protocolo3):
    anterior = [protocolo1, protocolo2]
    proxima = [protocolo2, protocolo3]

    resultado = compara_lista_protocolos(anterior, proxima)

    assert len(resultado['adicoes']) == 1
    assert resultado['adicoes'][0] == protocolo3

    assert len(resultado['exclusoes']) == 1
    assert resultado['exclusoes'][0] == protocolo1


def test_changes_between(produto, protocolo1, protocolo2, protocolo3):
    validated_data = {
        'eh_para_alunos_com_dieta':False,
        'componentes':"Componente3, Componente4",
        'tem_aditivos_alergenicos':False,
        'tipo':"Tipo1",
        'embalagem':"Embalagem X",
        'prazo_validade':"Alguns dias",
        'info_armazenamento':"Bote na geladeira",
        'outras_informacoes':"Produto do bom",
        'numero_registro':"123123123",
        'porcao':"5 cuias",
        'unidade_caseira':"Unidade3",
        'marca': mommy.make('Marca'),
        'protocolos': [protocolo1, protocolo3]
    }
    changes = changes_between(produto, validated_data)
    assert changes['componentes'] == {'de':'Componente1, Componente2','para':'Componente3, Componente4'}
    assert changes['info_armazenamento'] == {'de':'Guardem bem','para':'Bote na geladeira'}
    assert changes['eh_para_alunos_com_dieta'] == {'de':True,'para':False}
    assert changes['marca'] == {'de':produto.marca.uuid,'para':validated_data['marca'].uuid}

    resultado = changes['protocolos']

    assert len(resultado['adicoes']) == 1
    assert resultado['adicoes'][0] == protocolo3

    assert len(resultado['exclusoes']) == 1
    assert resultado['exclusoes'][0] == protocolo2
