import datetime

from freezegun import freeze_time
from rest_framework import status

from ...dados_comuns.constants import SEM_FILTRO
from ..api.constants import (
    AGUARDANDO_CODAE,
    AUTORIZADOS,
    CANCELADOS,
    INCLUSOES_AUTORIZADAS,
    NEGADOS,
    PENDENTES_AUTORIZACAO,
    PENDENTES_VALIDACAO_DRE,
    PESQUISA,
    RELATORIO_PERIODO,
    RELATORIO_RESUMO_MES_ANO,
    RESUMO_ANO,
    RESUMO_MES,
    TIPO_VISAO_SOLICITACOES
)


def base_diretoria_regional(client_autenticado_dre, resource):
    endpoint = f'/diretoria-regional-solicitacoes/{resource}/'
    response = client_autenticado_dre.get(endpoint)
    assert response.status_code == status.HTTP_200_OK
    return response


def base_codae(client_autenticado, resource):
    endpoint = f'/codae-solicitacoes/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_painel_dre_pendentes_validacao(client_autenticado_dre_paineis_consolidados):
    response = base_diretoria_regional(client_autenticado_dre_paineis_consolidados,
                                       f'{PENDENTES_VALIDACAO_DRE}/{SEM_FILTRO}/{TIPO_VISAO_SOLICITACOES}')
    # TODO: Revisar esse teste, vive dando problema pois os valores sempre se alteram
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_painel_dre_aguardando_codae(client_autenticado_dre_paineis_consolidados):
    response = base_diretoria_regional(client_autenticado_dre_paineis_consolidados, f'{AGUARDANDO_CODAE}')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_painel_codae_pendentes_autorizacao(client_autenticado_codae_gestao_alimentacao):
    base_codae(client_autenticado_codae_gestao_alimentacao, f'{PENDENTES_AUTORIZACAO}/{SEM_FILTRO}')


def test_url_endpoint_painel_codae_aprovados(client_autenticado_codae_gestao_alimentacao):
    base_codae(client_autenticado_codae_gestao_alimentacao, AUTORIZADOS)


def test_url_endpoint_painel_codae_cancelados(client_autenticado_codae_gestao_alimentacao):
    base_codae(client_autenticado_codae_gestao_alimentacao, CANCELADOS)


def test_url_endpoint_painel_codae_negados(client_autenticado_codae_gestao_alimentacao):
    base_codae(client_autenticado_codae_gestao_alimentacao, NEGADOS)


def test_dieta_especial_solicitacoes_viewset_pendentes(client_autenticado,
                                                       solicitacoes_dieta_especial,
                                                       status_and_endpoint):
    wf_status, endpoint = status_and_endpoint
    response = client_autenticado.get(f'/dieta-especial/{endpoint}/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['count'] == 2


@freeze_time('2019-10-11')
def test_escola_relatorio_evolucao_solicitacoes(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    response = client.get(
        f'/escola-solicitacoes/{RESUMO_ANO}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'results':
            {'total': 10,
             'Inclusão de Alimentação': {'quantidades': [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 3},
             'Alteração do tipo de Alimentação': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3], 'total': 3},
             'Inversão de dia de Cardápio': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
             'Suspensão de Alimentação': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
             'Kit Lanche Passeio': {'quantidades': [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0], 'total': 4},
             'Kit Lanche Passeio Unificado': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
             'Dieta Especial': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0}
             }
    }


@freeze_time('2019-02-11')
def test_filtro_escola(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    tipo = 'INC_ALIMENTA_CONTINUA'
    response = client.get(
        f'/escola-solicitacoes/{PESQUISA}/?tipo_solicitacao={tipo}'
        f'&data_inicial=2019-02-01&data_final=2019-02-28&status_solicitacao=TODOS')
    assert response.status_code == status.HTTP_200_OK
    for i in response.json()['results']:
        assert i['tipo_doc'] == tipo


@freeze_time('2019-02-11')
def test_relatorio_filtro_escola(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    tipo = 'INC_ALIMENTA_CONTINUA'
    response = client.get(
        f'/escola-solicitacoes/{RELATORIO_PERIODO}/?tipo_solicitacao={tipo}'
        f'&data_inicial=2019-02-01&data_final=2019-02-28&status_solicitacao=TODOS')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'application/pdf'
    assert response.headers[
        'content-disposition'] == 'filename="relatorio_filtro_de_2019-02-01 00:00:00_ate_2019-02-28 00:00:00.pdf"'
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


@freeze_time('2019-02-11')
def test_relatorio_mes_ano_escola(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    response = client.get(
        f'/escola-solicitacoes/{RELATORIO_RESUMO_MES_ANO}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'application/pdf'
    assert response.headers['content-disposition'] == 'filename="relatorio_resumo_anual_e_mensal.pdf"'
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


@freeze_time('2019-02-11')
def test_relatorio_filtro_escola_error(users_diretor_escola):
    client, email, password, rf, cpf, user = users_diretor_escola
    tipo = 'INCLUSAO_QUE_NAO_EXISTE'
    status_solicitacao = 'TESTE_XXX'
    response = client.get(
        f'/escola-solicitacoes/{RELATORIO_PERIODO}/?tipo_solicitacao={tipo}'
        f'&data_inicial=20190201&data_final=20190228&status_solicitacao={status_solicitacao}')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.headers['content-type'] == 'application/json'
    assert response.json() == {
        'tipo_solicitacao': [
            'tipo de solicitação INCLUSAO_QUE_NAO_EXISTE não permitida, deve ser um dos: '
            "['ALT_CARDAPIO', 'INV_CARDAPIO', 'INC_ALIMENTA', 'INC_ALIMENTA_CONTINUA', 'KIT_LANCHE_AVULSA',"
            " 'SUSP_ALIMENTACAO', 'KIT_LANCHE_UNIFICADA', 'TODOS']"
        ],
        'status_solicitacao': [
            'status de solicitação TESTE_XXX não permitida, deve ser um dos: '
            "['AUTORIZADOS', 'NEGADOS', 'CANCELADOS', 'RECEBIDAS', 'TODOS']"
        ],
        'data_inicial': ['Informe uma data válida.'], 'data_final': ['Informe uma data válida.']
    }


@freeze_time('2019-10-11')
def test_resumo_ano_dre(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    response = client.get(
        f'/diretoria-regional-solicitacoes/{RESUMO_ANO}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'results': {'total': 10,
                    'Inclusão de Alimentação': {'quantidades': [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 3},
                    'Alteração do tipo de Alimentação': {
                        'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3], 'total': 3},
                    'Inversão de dia de Cardápio': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                    'Suspensão de Alimentação': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                    'Kit Lanche Passeio': {'quantidades': [0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 4},
                    'Kit Lanche Passeio Unificado': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                    'Dieta Especial': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0}
                    }
    }


@freeze_time('2019-02-11')
def test_resumo_mes_dre(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    response = client.get(
        f'/diretoria-regional-solicitacoes/{RESUMO_MES}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'total_autorizados': 0, 'total_negados': 0, 'total_cancelados': 0, 'total_pendentes': 2,
                               'total_mes_atual': 2, 'total_autorizados_mes_passado': 0, 'total_negados_mes_passado': 1,
                               'total_cancelados_mes_passado': 0, 'total_pendentes_mes_passado': 2,
                               'total_mes_passado': 3}


@freeze_time('2019-02-11')
def test_filtro_dre(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    escola = 'TODOS'
    response = client.get(
        f'/diretoria-regional-solicitacoes/{PESQUISA}/{escola}/?tipo_solicitacao=TODOS'
        f'&data_inicial=2019-02-01&data_final=2019-02-28&status_solicitacao=TODOS')
    assert response.status_code == status.HTTP_200_OK
    for i in response.json()['results']:
        assert datetime.datetime.strptime(i['criado_em'], '%d/%m/%Y %H:%M:%S').month == 2
    tipo_solicitacao = 'KIT_LANCHE_AVULSA'
    response = client.get(
        f'/diretoria-regional-solicitacoes/{PESQUISA}/{escola}/?tipo_solicitacao={tipo_solicitacao}'
        f'&data_inicial=2019-02-01&data_final=2019-02-28&status_solicitacao=TODOS')
    assert response.status_code == status.HTTP_200_OK
    for i in response.json()['results']:
        assert i['tipo_doc'] == tipo_solicitacao


@freeze_time('2019-02-11')
def test_relatorio_filtro_dre(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    escola = 'TODOS'
    response = client.get(
        f'/diretoria-regional-solicitacoes/{RELATORIO_PERIODO}/{escola}/?tipo_solicitacao=TODOS'
        f'&data_inicial=2019-02-01&data_final=2019-02-28&status_solicitacao=TODOS')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'application/pdf'
    assert response.headers[
        'content-disposition'
    ] == 'filename="relatorio_filtro_de_2019-02-01 00:00:00_ate_2019-02-28 00:00:00.pdf"'
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


@freeze_time('2019-02-11')
def test_relatorio_mes_ano_dre(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    response = client.get(
        f'/diretoria-regional-solicitacoes/{RELATORIO_RESUMO_MES_ANO}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['content-type'] == 'application/pdf'
    assert response.headers['content-disposition'] == 'filename="relatorio_resumo_anual_e_mensal.pdf"'
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


@freeze_time('2019-02-11')
def test_relatorio_filtro_dre_error(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    escola = 'TESTE'
    tipo_solicitacao = 'QUALQUERUM'
    status_solicitacao = 'EM_APROVACAO'
    response = client.get(
        f'/diretoria-regional-solicitacoes/{RELATORIO_PERIODO}/{escola}/?tipo_solicitacao={tipo_solicitacao}'
        f'&data_inicial=20201008&data_final=2019-02-28&status_solicitacao={status_solicitacao}')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.headers['content-type'] == 'application/json'
    assert response.json() == {
        'tipo_solicitacao': [
            'tipo de solicitação QUALQUERUM não permitida, deve ser um dos: '
            "['ALT_CARDAPIO', 'INV_CARDAPIO', 'INC_ALIMENTA', 'INC_ALIMENTA_CONTINUA', 'KIT_LANCHE_AVULSA', "
            "'SUSP_ALIMENTACAO', 'KIT_LANCHE_UNIFICADA', 'TODOS']"
        ],
        'status_solicitacao': [
            'status de solicitação EM_APROVACAO não permitida, deve ser um dos: '
            "['AUTORIZADOS', 'NEGADOS', 'CANCELADOS', 'RECEBIDAS', 'TODOS']"
        ],
        'data_inicial': ['Informe uma data válida.']
    }


@freeze_time('2019-02-11')
def test_filtro_dre_error(solicitacoes_ano_dre):
    client, email, password, rf, cpf, user = solicitacoes_ano_dre
    escola = 'PARAMETRO_ERRADO'
    data_inicial = '01/02/2020'
    data_final = '2019/02/28'
    status_solicitacao = 'URGENTE'
    tipo = 'lanche pra funcionarios unificado'

    response = client.get(
        f'/diretoria-regional-solicitacoes/{PESQUISA}/{escola}/?tipo_solicitacao={tipo}'
        f'&data_inicial={data_inicial}&data_final={data_final}&status_solicitacao={status_solicitacao}')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'tipo_solicitacao': [
            'tipo de solicitação lanche pra funcionarios unificado não permitida, deve ser um dos: '
            "['ALT_CARDAPIO', 'INV_CARDAPIO', 'INC_ALIMENTA', 'INC_ALIMENTA_CONTINUA', 'KIT_LANCHE_AVULSA', "
            "'SUSP_ALIMENTACAO', 'KIT_LANCHE_UNIFICADA', 'TODOS']"],
        'status_solicitacao': [
            'status de solicitação URGENTE não permitida, deve ser um dos: '
            "['AUTORIZADOS', 'NEGADOS', 'CANCELADOS', 'RECEBIDAS', 'TODOS']"],
        'data_final': ['Informe uma data válida.']
    }


def test_ceu_gestao_periodos_com_solicitacoes_autorizadas(client_autenticado_escola_paineis_consolidados, escola):
    response = client_autenticado_escola_paineis_consolidados.get(
        '/escola-solicitacoes/ceu-gestao-periodos-com-solicitacoes-autorizadas/'
        f'?escola_uuid={escola.uuid}&mes=07&ano=2023'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['nome'] == 'MANHA'


def test_inclusoes_normais_autorizadas(client_autenticado_escola_paineis_consolidados, escola):
    response = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=07&ano=2023'
        f'&periodos_escolares[]=MANHA&excluir_inclusoes_continuas=true'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    assert response.data['results'][0]['numero_alunos'] == 100


def test_inclusoes_continuas_autorizadas(client_autenticado_escola_paineis_consolidados,
                                         escola, inclusao_alimentacao_continua):
    response = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=05&ano=2023'
        f'&periodos_escolares[]=MANHA&periodos_escolares[]=TARDE&tipo_doc=INC_ALIMENTA_CONTINUA'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 12
    assert response.data['results'][0]['dia'] == '20'
    assert response.data['results'][0]['numero_alunos'] == 50
    assert response.data['results'][len(response.data['results']) - 1]['dia'] == '31'


def test_inclusoes_cei_autorizadas(client_autenticado_escola_paineis_consolidados, escola, inclusao_alimentacao_cei):
    response_manha = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=08&ano=2023'
        f'&periodos_escolares[]=MANHA&excluir_inclusoes_continuas=true'
    )
    assert response_manha.status_code == status.HTTP_200_OK
    assert len(response_manha.data['results']) == 1
    assert response_manha.data['results'][0]['dia'] == 10

    response_parcial = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=08&ano=2023'
        f'&periodos_escolares[]=PARCIAL&excluir_inclusoes_continuas=true'
    )
    assert response_parcial.status_code == status.HTTP_200_OK
    assert len(response_parcial.data['results']) == 0

    response_integral = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=08&ano=2023'
        f'&periodos_escolares[]=INTEGRAL&excluir_inclusoes_continuas=true'
    )
    assert response_integral.status_code == status.HTTP_200_OK
    assert len(response_integral.data['results']) == 1
    assert response_manha.data['results'][0]['dia'] == 10

    response_tarde = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=08&ano=2023'
        f'&periodos_escolares[]=TARDE&excluir_inclusoes_continuas=true'
    )
    assert response_tarde.status_code == status.HTTP_200_OK
    assert len(response_tarde.data['results']) == 0
