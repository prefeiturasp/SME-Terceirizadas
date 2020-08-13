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
