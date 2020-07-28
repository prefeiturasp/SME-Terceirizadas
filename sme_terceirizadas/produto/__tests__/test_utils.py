from datetime import date

from ..utils import cria_filtro_produto_por_parametros_form


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
        'status': 'homologacoes__status__in'
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
