from datetime import date

from ..utils import get_config_cabecario_relatorio_analise


def test_config_cabecario_obter_cabecario_reduzido():
    filtros = {}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_REDUZIDO'


def test_config_cabecario_obter_cabecario_por_data():
    filtros = {'data_analise_inicial': date.today().strftime('%d/%m/%Y')}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_POR_DATA'

    filtros = {'data_analise_inicial': date.today().strftime('%d/%m/%Y'),
               'data_analise_final': date.today().strftime('%d/%m/%Y')}
    assert config['cabecario_tipo'] == 'CABECARIO_POR_DATA'
    config = get_config_cabecario_relatorio_analise(filtros, None, None)


def test_config_cabecario_obter_cabecario_por_nome_produto():
    filtros = {'nome_produto': 'Teste'}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_POR_NOME'


def test_config_cabecario_obter_cabecario_por_nome_marca():
    filtros = {'nome_marca': 'Teste'}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_POR_NOME'


def test_config_cabecario_obter_cabecario_por_nome_fabricante():
    filtros = {'nome_fabricante': 'Teste'}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_POR_NOME'


def test_config_cabecario_obter_cabecario_por_nome_terceirizada():
    filtros = {'nome_terceirizada': 'Teste'}
    contatos_terceirizada = {'email': 'teste@teste.com', 'telefone': '1199999999'}
    config = get_config_cabecario_relatorio_analise(filtros, None, contatos_terceirizada)
    assert config['cabecario_tipo'] == 'CABECARIO_POR_NOME_TERCEIRIZADA'
