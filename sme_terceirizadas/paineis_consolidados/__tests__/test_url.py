import datetime

from freezegun import freeze_time
from rest_framework import status

from ...dados_comuns.constants import SEM_FILTRO
from ...eol_servico.utils import EOLService
from ...escola.__tests__.conftest import mocked_informacoes_escola_turma_aluno
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
    SUSPENSOES_AUTORIZADAS,
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
                                         escola, inclusao_alimentacao_continua_entre_dois_meses,
                                         inclusao_alimentacao_continua_unico_mes,
                                         inclusao_alimentacao_continua_varios_meses):
    response_mes_03 = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=03&ano=2023'
        f'&periodos_escolares[]=MANHA&periodos_escolares[]=TARDE&tipo_doc=INC_ALIMENTA_CONTINUA'
    )
    assert response_mes_03.status_code == status.HTTP_200_OK
    assert len(response_mes_03.data['results']) == 12
    assert response_mes_03.data['results'][0]['dia'] == '20'
    assert response_mes_03.data['results'][0]['numero_alunos'] == 50
    assert response_mes_03.data['results'][len(response_mes_03.data['results']) - 1]['dia'] == '31'

    response_mes_04 = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=04&ano=2023'
        f'&periodos_escolares[]=MANHA&periodos_escolares[]=TARDE&tipo_doc=INC_ALIMENTA_CONTINUA'
    )
    assert response_mes_04.status_code == status.HTTP_200_OK
    assert len(response_mes_04.data['results']) == 10
    assert response_mes_04.data['results'][0]['dia'] == '01'
    assert response_mes_04.data['results'][0]['numero_alunos'] == 50
    assert response_mes_04.data['results'][len(response_mes_04.data['results']) - 1]['dia'] == '10'

    response_mes_02 = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=02&ano=2023'
        f'&periodos_escolares[]=MANHA&periodos_escolares[]=TARDE&tipo_doc=INC_ALIMENTA_CONTINUA'
    )
    assert response_mes_02.status_code == status.HTTP_200_OK
    assert len(response_mes_02.data['results']) == 21
    assert response_mes_02.data['results'][0]['dia'] == '05'
    assert response_mes_02.data['results'][0]['numero_alunos'] == 100
    assert response_mes_02.data['results'][len(response_mes_02.data['results']) - 1]['dia'] == '25'

    response_mes_07 = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{INCLUSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Inclusão de&mes=07&ano=2023'
        f'&periodos_escolares[]=MANHA&periodos_escolares[]=TARDE&tipo_doc=INC_ALIMENTA_CONTINUA'
    )
    assert response_mes_07.status_code == status.HTTP_200_OK
    assert len(response_mes_07.data['results']) == 31
    assert response_mes_07.data['results'][0]['dia'] == '01'
    assert response_mes_07.data['results'][0]['numero_alunos'] == 75
    assert response_mes_07.data['results'][len(response_mes_07.data['results']) - 1]['dia'] == '31'


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


def test_suspensoes_autorizadas(client_autenticado_escola_paineis_consolidados,
                                escola, suspensoes_alimentacao):
    response_manha_cei = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{SUSPENSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Suspensão&mes=07&ano=2023'
        f'&nome_periodo_escolar=MANHA'
    )
    assert response_manha_cei.status_code == status.HTTP_200_OK
    assert len(response_manha_cei.data['results']) == 1
    assert response_manha_cei.data['results'][0]['dia'] == '15'
    assert response_manha_cei.data['results'][0]['periodo'] == 'MANHA'

    response_parcial_cei = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{SUSPENSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Suspensão&mes=07&ano=2023'
        f'&nome_periodo_escolar=PARCIAL'
    )
    assert response_parcial_cei.status_code == status.HTTP_200_OK
    assert len(response_parcial_cei.data['results']) == 1
    assert response_parcial_cei.data['results'][0]['dia'] == '15'
    assert response_parcial_cei.data['results'][0]['periodo'] == 'INTEGRAL'

    response_suspensao_manha = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{SUSPENSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Suspensão&mes=08&ano=2023'
        f'&nome_periodo_escolar=MANHA'
    )
    assert response_suspensao_manha.status_code == status.HTTP_200_OK
    assert len(response_suspensao_manha.data['results']) == 2
    assert response_suspensao_manha.data['results'][0]['numero_alunos'] == 75
    assert response_suspensao_manha.data['results'][0]['periodo'] == 'MANHA'

    response_suspensao_integral = client_autenticado_escola_paineis_consolidados.get(
        f'/escola-solicitacoes/{SUSPENSOES_AUTORIZADAS}/'
        f'?escola_uuid={escola.uuid}&tipo_solicitacao=Suspensão&mes=08&ano=2023'
        f'&nome_periodo_escolar=INTEGRAL'
    )
    assert response_suspensao_integral.status_code == status.HTTP_200_OK
    assert len(response_suspensao_integral.data['results']) == 2
    assert response_suspensao_integral.data['results'][0]['numero_alunos'] == 50
    assert response_suspensao_integral.data['results'][0]['periodo'] == 'INTEGRAL'


def test_solicitacoes_detalhadas_inc_alimentacao(
        client_autenticado_escola_paineis_consolidados, inclusoes_normais, inclusao_alimentacao_continua_unico_mes,
        inclusao_alimentacao_cei, inclusao_alimentacao_cemei, monkeypatch):
    monkeypatch.setattr(EOLService, 'get_informacoes_escola_turma_aluno',
                        lambda p1: mocked_informacoes_escola_turma_aluno())
    response = client_autenticado_escola_paineis_consolidados.get(
        f'/solicitacoes-genericas/solicitacoes-detalhadas/'
        f'?solicitacoes[]='
        f'%7B%22tipo_doc%22:%22INC_ALIMENTA%22,%22uuid%22:%22a4639e26-f4fd-43e9-a8cc-2d0da995c8ef%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22INC_ALIMENTA_CONTINUA%22,%22uuid%22:%22ec27137e-9b8f-419c-adaa-7ed238d40bae%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22INC_ALIMENTA_CEI%22,%22uuid%22:%2250830aed-33ad-442a-8890-5b508e54a0d8%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22INC_ALIMENTA_CEMEI%22,%22uuid%22:%22ba5551b3-b770-412b-a923-b0e78301d1fd%22%7D'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['data']) == 4


def test_solicitacoes_detalhadas_kit_lanche(
        client_autenticado_escola_paineis_consolidados, solicitacoes_kit_lanche, solicitacao_unificada, kit_lanche_cei,
        kit_lanche_cemei, monkeypatch):
    monkeypatch.setattr(EOLService, 'get_informacoes_escola_turma_aluno',
                        lambda p1: mocked_informacoes_escola_turma_aluno())
    response = client_autenticado_escola_paineis_consolidados.get(
        f'/solicitacoes-genericas/solicitacoes-detalhadas/'
        f'?solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_AVULSA%22,%22uuid%22:%22ac0b6f5b-36b0-47d2-99a2-3bc9825b31fb%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_AVULSA%22,%22uuid%22:%22d15f17d5-d4c5-47f5-a09a-55677dbc65bf%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_AVULSA%22,%22uuid%22:%22c9715ddb-7e95-4156-91a5-c60c8621806b%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_AVULSA%22,%22uuid%22:%228827b394-ef39-4757-8136-6e09d5c7c486%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_UNIFICADA%22,%22uuid%22:%22d0d3ec92-a2db-4060-a4da-b7ed9d88a7c3%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_AVULSA_CEI%22,%22uuid%22:%22318ca781-943a-4121-b970-70ac4d4ccc8a%22%7D'
        f'&solicitacoes[]='
        f'%7B%22tipo_doc%22:%22KIT_LANCHE_CEMEI%22,%22uuid%22:%222fdb22fe-370c-4379-94f4-a52478c03e6e%22%7D'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['data']) == 7
