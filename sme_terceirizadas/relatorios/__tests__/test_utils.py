from ..utils import get_config_cabecario_relatorio_analise


def test_config_cabecario_obter_cabecario_reduzido():
    filtros = {}
    config = get_config_cabecario_relatorio_analise(filtros, None, None)
    assert config['cabecario_tipo'] == 'CABECARIO_REDUZIDO'
