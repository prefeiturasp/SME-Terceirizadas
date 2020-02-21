from rest_framework import status

from ..models import FaixaEtaria, MudancaFaixasEtarias

ENDPOINT_ALUNOS_POR_PERIODO = 'quantidade-alunos-por-periodo'
ENDPOINT_LOTES = 'lotes'


def test_url_endpoint_quantidade_alunos_por_periodo(client_autenticado, escola):
    response = client_autenticado.get(
        f'/{ENDPOINT_ALUNOS_POR_PERIODO}/escola/{escola.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_lotes(client_autenticado):
    response = client_autenticado.get(
        f'/{ENDPOINT_LOTES}/'
    )
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_lotes_delete(client_autenticado, lote):
    response = client_autenticado.delete(
        f'/{ENDPOINT_LOTES}/{lote.uuid}/'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_alunos_por_faixa_etaria_data_invalida(client_autenticado, escola_periodo_escolar):
    url = f'/quantidade-alunos-por-periodo/{escola_periodo_escolar.uuid}/alunos-por-faixa-etaria/2020-15-40/'
    response = client_autenticado.get(url)
    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert 'data_referencia' in json
    assert json['data_referencia'][0] == 'Informe uma data válida.'


def test_url_endpoint_alunos_por_faixa_etaria_data_valida(client_autenticado, escola_periodo_escolar):
    url = f'/quantidade-alunos-por-periodo/{escola_periodo_escolar.uuid}/alunos-por-faixa-etaria/2020-10-20/'
    response = client_autenticado.get(url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_url_endpoint_cria_mudanca_faixa_etaria(client_autenticado_coordenador_codae):
    data = {
        'faixas_etarias_ativadas': [
            {'inicio': 1, 'fim': 4},
            {'inicio': 4, 'fim': 8},
            {'inicio': 8, 'fim': 12},
            {'inicio': 12, 'fim': 17}
        ],
        'justificativa': 'Primeiro cadastro'
    }
    response = client_autenticado_coordenador_codae.post(
        '/faixas-etarias/',
        content_type='application/json',
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED

    assert MudancaFaixasEtarias.objects.count() == 1
    assert FaixaEtaria.objects.count() == 4

    mfe = MudancaFaixasEtarias.objects.first()

    assert mfe.justificativa == data['justificativa']

    faixas_etarias = FaixaEtaria.objects.filter(ativo=True).order_by('inicio')
    for (expected, actual) in zip(data['faixas_etarias_ativadas'], faixas_etarias):
        assert expected['inicio'] == actual.inicio
        assert expected['fim'] == actual.fim


def test_url_endpoint_cria_mudanca_faixa_etaria_erro_fim_menor_igual_inicio(client_autenticado_coordenador_codae):
    faixas_etarias = [
        {'inicio': 10, 'fim': 5}
    ]
    response = client_autenticado_coordenador_codae.post(
        '/faixas-etarias/',
        content_type='application/json',
        data={'faixas_etarias_ativadas': faixas_etarias, 'justificativa': 'Primeiro cadastro'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (str(response.data['faixas_etarias_ativadas'][0]['non_field_errors'][0])
            ==
            'A faixa etária tem que terminar depois do início: inicio=10;fim=5')


def test_url_endpoint_cria_mudanca_faixa_etaria_erro_inicio_menor_zero(client_autenticado_coordenador_codae):
    faixas_etarias = [
        {'inicio': -10, 'fim': 5}
    ]
    response = client_autenticado_coordenador_codae.post(
        '/faixas-etarias/',
        content_type='application/json',
        data={'faixas_etarias_ativadas': faixas_etarias, 'justificativa': 'Primeiro cadastro'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert (str(response.data['faixas_etarias_ativadas'][0]['inicio'][0])
            ==
            'Certifque-se de que este valor seja maior ou igual a 0.')


def test_url_endpoint_lista_faixas_etarias(client_autenticado_coordenador_codae, faixas_etarias):
    response = client_autenticado_coordenador_codae.get('/faixas-etarias/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    ativas = FaixaEtaria.objects.filter(ativo=True)

    assert json['count'] == len(ativas)

    for (expected, actual) in zip(ativas, json['results']):
        assert actual['inicio'] == expected.inicio
        assert actual['fim'] == expected.fim
