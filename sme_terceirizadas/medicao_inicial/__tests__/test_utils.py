from calendar import monthrange
from collections import defaultdict

import pytest

from sme_terceirizadas.medicao_inicial.utils import (
    build_dict_relacao_categorias_e_campos,
    build_dict_relacao_categorias_e_campos_cei,
    build_headers_tabelas,
    build_headers_tabelas_cei,
    build_row_primeira_tabela,
    build_tabela_somatorio_body,
    build_tabelas_relatorio_medicao,
    build_tabelas_relatorio_medicao_cemei,
    get_lista_categorias_campos,
    get_lista_categorias_campos_cei,
    get_lista_dias_letivos,
    get_nome_campo,
    get_nome_periodo,
    get_somatorio_etec,
    get_somatorio_integral,
    get_somatorio_manha,
    get_somatorio_noite_eja,
    get_somatorio_programas_e_projetos,
    get_somatorio_solicitacoes_de_alimentacao,
    get_somatorio_tarde,
    get_somatorio_total_tabela,
    tratar_valores,
)

pytestmark = pytest.mark.django_db


def test_utils_build_dict_relacao_categorias_e_campos(
    solicitacao_medicao_inicial_varios_valores,
):
    assert build_dict_relacao_categorias_e_campos(
        solicitacao_medicao_inicial_varios_valores.medicoes.get(
            periodo_escolar__nome="MANHA"
        )
    ) == {
        "ALIMENTAÇÃO": [
            "matriculados",
            "total_refeicoes_pagamento",
            "total_sobremesas_pagamento",
            "lanche",
            "lanche_emergencial",
            "refeicao",
            "sobremesa",
        ],
        "DIETA ESPECIAL - TIPO A ENTERAL": [
            "aprovadas",
            "lanche",
            "lanche_emergencial",
            "refeicao",
            "sobremesa",
        ],
        "DIETA ESPECIAL - TIPO B": [
            "aprovadas",
            "lanche",
            "lanche_emergencial",
            "refeicao",
            "sobremesa",
        ],
    }


def test_utils_build_headers_tabelas(solicitacao_medicao_inicial_varios_valores):
    assert build_headers_tabelas(solicitacao_medicao_inicial_varios_valores) == [
        {
            "periodos": ["MANHA"],
            "categorias": ["ALIMENTAÇÃO", "DIETA ESPECIAL - TIPO A ENTERAL"],
            "nomes_campos": [
                "matriculados",
                "lanche",
                "refeicao",
                "total_refeicoes_pagamento",
                "sobremesa",
                "total_sobremesas_pagamento",
                "lanche_emergencial",
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
            ],
            "len_periodos": [12],
            "len_categorias": [7, 5],
            "valores_campos": [],
            "ordem_periodos_grupos": [1],
            "dias_letivos": [],
            "categorias_dos_periodos": {
                "MANHA": [
                    {"categoria": "ALIMENTAÇÃO", "numero_campos": 7},
                    {
                        "categoria": "DIETA ESPECIAL - TIPO A ENTERAL",
                        "numero_campos": 5,
                    },
                ]
            },
        },
        {
            "periodos": ["MANHA", "TARDE"],
            "categorias": ["DIETA ESPECIAL - TIPO B", "ALIMENTAÇÃO"],
            "nomes_campos": [
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
                "matriculados",
                "lanche",
                "refeicao",
                "total_refeicoes_pagamento",
                "sobremesa",
                "total_sobremesas_pagamento",
                "lanche_emergencial",
            ],
            "len_periodos": [5, 7],
            "len_categorias": [5, 7],
            "valores_campos": [],
            "ordem_periodos_grupos": [1, 2],
            "dias_letivos": [],
            "categorias_dos_periodos": {
                "MANHA": [{"categoria": "DIETA ESPECIAL - TIPO B", "numero_campos": 5}],
                "TARDE": [{"categoria": "ALIMENTAÇÃO", "numero_campos": 7}],
            },
        },
        {
            "periodos": ["TARDE"],
            "categorias": [
                "DIETA ESPECIAL - TIPO A ENTERAL",
                "DIETA ESPECIAL - TIPO B",
            ],
            "nomes_campos": [
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
            ],
            "len_periodos": [10],
            "len_categorias": [5, 5],
            "valores_campos": [],
            "ordem_periodos_grupos": [2],
            "dias_letivos": [],
            "categorias_dos_periodos": {
                "TARDE": [
                    {
                        "categoria": "DIETA ESPECIAL - TIPO A ENTERAL",
                        "numero_campos": 5,
                    },
                    {"categoria": "DIETA ESPECIAL - TIPO B", "numero_campos": 5},
                ]
            },
        },
    ]


def test_build_headers_tabelas_cei(
    solicitacao_medicao_inicial_valores_cei,
):
    assert build_headers_tabelas_cei(solicitacao_medicao_inicial_valores_cei) == [
        {
            "periodos": ["INTEGRAL", "MANHA"],
            "categorias": [
                {"categoria": "ALIMENTAÇÃO", "faixas_etarias": ["01 a 09 meses"]}
            ],
            "len_periodos": [2, 0],
            "len_categorias": [2],
            "valores_campos": [],
            "ordem_periodos_grupos": [1, 3],
            "periodo_values": defaultdict(int, {"INTEGRAL": 2, "MANHA": 0}),
            "categoria_values": defaultdict(int, {"ALIMENTAÇÃO": 2}),
        },
    ]


def test_get_lista_dias_letivos(solicitacao_medicao_inicial_varios_valores):
    dias_letivos = get_lista_dias_letivos(solicitacao_medicao_inicial_varios_valores)

    _, num_dias = monthrange(
        int(solicitacao_medicao_inicial_varios_valores.ano),
        int(solicitacao_medicao_inicial_varios_valores.mes),
    )

    assert len(dias_letivos) == num_dias


def test_get_nome_periodo():
    assert get_nome_periodo("Infantil INTEGRAL") == "INTEGRAL"
    assert get_nome_periodo("Infantil MANHA") == "MANHA"
    assert get_nome_periodo("Infantil TARDE") == "TARDE"
    assert get_nome_periodo("Fundamental MANHA") == "Fundamental MANHA"
    assert get_nome_periodo("EJA NOITE") == "EJA NOITE"


def test_build_tabelas_relatorio_medicao(solicitacao_medicao_inicial_varios_valores):
    assert build_tabelas_relatorio_medicao(
        solicitacao_medicao_inicial_varios_valores
    ) == [
        {
            "periodos": ["MANHA"],
            "categorias": ["ALIMENTAÇÃO", "DIETA ESPECIAL - TIPO A ENTERAL"],
            "nomes_campos": [
                "matriculados",
                "lanche",
                "refeicao",
                "total_refeicoes_pagamento",
                "sobremesa",
                "total_sobremesas_pagamento",
                "lanche_emergencial",
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
            ],
            "len_periodos": [12],
            "len_categorias": [7, 5],
            "valores_campos": [
                [1, "0", "10", "10", "0", "10", "0", "10", "0", "10", "10", "10", "10"],
                [2, "0", "10", "10", "0", "10", "0", "10", "0", "10", "10", "10", "10"],
                [3, "0", "10", "10", "0", "10", "0", "10", "0", "10", "10", "10", "10"],
                [4, "0", "10", "10", "0", "10", "0", "10", "0", "10", "10", "10", "10"],
                [5, "0", "10", "10", "0", "10", "0", "10", "0", "10", "10", "10", "10"],
                [6, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [7, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [8, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [9, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [10, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [11, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [12, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [13, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [14, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [15, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [16, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [17, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [18, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [19, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [20, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [21, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [22, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [23, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [24, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [25, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [26, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [27, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [28, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [29, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [30, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [31, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                ["Total", "-", 50, 50, 0, 50, 0, 50, "-", 50, 50, 50, 50],
            ],
            "ordem_periodos_grupos": [1],
            "dias_letivos": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "categorias_dos_periodos": {
                "MANHA": [
                    {"categoria": "ALIMENTAÇÃO", "numero_campos": 7},
                    {
                        "categoria": "DIETA ESPECIAL - TIPO A ENTERAL",
                        "numero_campos": 5,
                    },
                ]
            },
        },
        {
            "periodos": ["MANHA", "TARDE"],
            "categorias": ["DIETA ESPECIAL - TIPO B", "ALIMENTAÇÃO"],
            "nomes_campos": [
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
                "matriculados",
                "lanche",
                "refeicao",
                "total_refeicoes_pagamento",
                "sobremesa",
                "total_sobremesas_pagamento",
                "lanche_emergencial",
            ],
            "len_periodos": [5, 7],
            "len_categorias": [5, 7],
            "valores_campos": [
                [1, "0", "10", "10", "10", "10", "0", "10", "10", "0", "10", "0", "10"],
                [2, "0", "10", "10", "10", "10", "0", "10", "10", "0", "10", "0", "10"],
                [3, "0", "10", "10", "10", "10", "0", "10", "10", "0", "10", "0", "10"],
                [4, "0", "10", "10", "10", "10", "0", "10", "10", "0", "10", "0", "10"],
                [5, "0", "10", "10", "10", "10", "0", "10", "10", "0", "10", "0", "10"],
                [6, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [7, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [8, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [9, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [10, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [11, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [12, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [13, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [14, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [15, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [16, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [17, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [18, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [19, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [20, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [21, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [22, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [23, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [24, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [25, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [26, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [27, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [28, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [29, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [30, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [31, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                ["Total", "-", 50, 50, 50, 50, "-", 50, 50, 0, 50, 0, 50],
            ],
            "ordem_periodos_grupos": [1, 2],
            "dias_letivos": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "categorias_dos_periodos": {
                "MANHA": [{"categoria": "DIETA ESPECIAL - TIPO B", "numero_campos": 5}],
                "TARDE": [{"categoria": "ALIMENTAÇÃO", "numero_campos": 7}],
            },
        },
        {
            "periodos": ["TARDE"],
            "categorias": [
                "DIETA ESPECIAL - TIPO A ENTERAL",
                "DIETA ESPECIAL - TIPO B",
            ],
            "nomes_campos": [
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
                "aprovadas",
                "lanche",
                "refeicao",
                "sobremesa",
                "lanche_emergencial",
            ],
            "len_periodos": [10],
            "len_categorias": [5, 5],
            "valores_campos": [
                [1, "0", "10", "10", "10", "10", "0", "10", "10", "10", "10"],
                [2, "0", "10", "10", "10", "10", "0", "10", "10", "10", "10"],
                [3, "0", "10", "10", "10", "10", "0", "10", "10", "10", "10"],
                [4, "0", "10", "10", "10", "10", "0", "10", "10", "10", "10"],
                [5, "0", "10", "10", "10", "10", "0", "10", "10", "10", "10"],
                [6, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [7, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [8, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [9, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [10, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [11, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [12, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [13, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [14, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [15, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [16, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [17, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [18, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [19, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [20, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [21, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [22, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [23, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [24, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [25, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [26, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [27, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [28, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [29, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [30, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                [31, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                ["Total", "-", 50, 50, 50, 50, "-", 50, 50, 50, 50],
            ],
            "ordem_periodos_grupos": [2],
            "dias_letivos": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "categorias_dos_periodos": {
                "TARDE": [
                    {
                        "categoria": "DIETA ESPECIAL - TIPO A ENTERAL",
                        "numero_campos": 5,
                    },
                    {"categoria": "DIETA ESPECIAL - TIPO B", "numero_campos": 5},
                ]
            },
        },
    ]


def test_utils_get_lista_categorias_campos(medicao_solicitacoes_alimentacao):
    assert get_lista_categorias_campos(medicao_solicitacoes_alimentacao) == [
        ("LANCHE EMERGENCIAL", "solicitado"),
        ("LANCHE EMERGENCIAL", "consumido"),
        ("KIT LANCHE", "solicitado"),
        ("KIT LANCHE", "consumido"),
    ]


def test_utils_get_lista_categorias_campos_cei(medicao_solicitacoes_alimentacao_cei):
    assert get_lista_categorias_campos_cei(medicao_solicitacoes_alimentacao_cei) == [
        ("ALIMENTAÇÃO", "01 a 02 meses")
    ]


def test_build_dict_relacao_categorias_e_campos_cei(
    medicao_solicitacoes_alimentacao_cei,
):
    assert build_dict_relacao_categorias_e_campos_cei(
        medicao_solicitacoes_alimentacao_cei
    ) == {"ALIMENTAÇÃO": ["01 a 02 meses"]}


def test_utils_tratar_valores(escola, escola_emei):
    campos = [
        "lanche",
        "refeicao",
        "lanche_emergencial",
        "sobremesa",
        "repeticao_refeicao",
        "kit_lanche",
        "repeticao_sobremesa",
        "2_lanche_5h",
        "2_lanche_4h",
        "2_refeicao_1_oferta",
        "repeticao_2_refeicao",
        "2_sobremesa_1_oferta",
        "repeticao_2_sobremesa",
    ]
    total_por_nome_campo = {campo: 10 for campo in campos}
    assert tratar_valores(escola_emei, total_por_nome_campo) == {
        "lanche_emergencial": 10,
        "kit_lanche": 10,
        "lanche": 20,
        "lanche_4h": 10,
        "refeicao": 20,
        "sobremesa": 20,
    }
    assert tratar_valores(escola, total_por_nome_campo) == {
        "lanche_emergencial": 10,
        "kit_lanche": 10,
        "lanche": 20,
        "lanche_4h": 10,
        "refeicao": 40,
        "sobremesa": 40,
    }


def test_utils_get_nome_campo():
    assert get_nome_campo("lanche_4h") == "Lanche 4h"
    assert get_nome_campo("repeticao_sobremesa") == "Repetição de Sobremesa"


def test_utils_get_somatorio_manha(solicitacao_medicao_inicial_com_valores_repeticao):
    assert (
        get_somatorio_manha(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_manha(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_manha(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_utils_get_somatorio_tarde(solicitacao_medicao_inicial_com_valores_repeticao):
    assert (
        get_somatorio_tarde(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_tarde(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_tarde(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_utils_get_somatorio_integral(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    assert (
        get_somatorio_integral(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_integral(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_integral(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_build_tabelas_relatorio_medicao_cemei(solicitacao_medicao_inicial_cemei):
    assert build_tabelas_relatorio_medicao_cemei(solicitacao_medicao_inicial_cemei) == [
        {
            "periodos": ["INTEGRAL"],
            "categorias": ["ALIMENTAÇÃO"],
            "nomes_campos": [],
            "faixas_etarias": ["01 mês", "total"],
            "len_periodos": [3],
            "len_categorias": [3],
            "valores_campos": [
                [1, "0", "10", "10"],
                [2, "0", "0", "0"],
                [3, "0", "0", "0"],
                [4, "0", "0", "0"],
                [5, "0", "0", "0"],
                [6, "0", "0", "0"],
                [7, "0", "0", "0"],
                [8, "0", "0", "0"],
                [9, "0", "0", "0"],
                [10, "0", "0", "0"],
                [11, "0", "0", "0"],
                [12, "0", "0", "0"],
                [13, "0", "0", "0"],
                [14, "0", "0", "0"],
                [15, "0", "0", "0"],
                [16, "0", "0", "0"],
                [17, "0", "0", "0"],
                [18, "0", "0", "0"],
                [19, "0", "0", "0"],
                [20, "0", "0", "0"],
                [21, "0", "0", "0"],
                [22, "0", "0", "0"],
                [23, "0", "0", "0"],
                [24, "0", "0", "0"],
                [25, "0", "0", "0"],
                [26, "0", "0", "0"],
                [27, "0", "0", "0"],
                [28, "0", "0", "0"],
                [29, "0", "0", "0"],
                [30, "0", "0", "0"],
                ["Total", "-", "10", "10"],
            ],
            "ordem_periodos_grupos": [1],
            "dias_letivos": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "categorias_dos_periodos": {
                "INTEGRAL": [{"categoria": "ALIMENTAÇÃO", "numero_campos": 1}]
            },
        }
    ]


def test_utils_get_somatorio_noite_eja(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    assert (
        get_somatorio_noite_eja(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_noite_eja(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_noite_eja(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_utils_get_somatorio_etec(solicitacao_medicao_inicial_com_valores_repeticao):
    assert (
        get_somatorio_etec(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_etec(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_etec(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_utils_get_somatorio_solicitacoes_de_alimentacao(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    solicitacao = solicitacao_medicao_inicial_com_valores_repeticao
    assert (
        get_somatorio_solicitacoes_de_alimentacao("lanche_emergencial", solicitacao)
        == 50
    )
    assert get_somatorio_solicitacoes_de_alimentacao("kit_lanche", solicitacao) == 50
    assert get_somatorio_solicitacoes_de_alimentacao("lanche_4h", solicitacao) == " - "


def test_utils_get_somatorio_programas_e_projetos(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    assert (
        get_somatorio_programas_e_projetos(
            "refeicao", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_programas_e_projetos(
            "sobremesa", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == 100
    )
    assert (
        get_somatorio_programas_e_projetos(
            "lanche_4h", solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
        )
        == " - "
    )


def test_utils_get_somatorio_total_tabela(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    solicitacao = solicitacao_medicao_inicial_com_valores_repeticao
    somatorio_manha = get_somatorio_manha("refeicao", solicitacao, {}, {})
    somatorio_tarde = get_somatorio_tarde("refeicao", solicitacao, {}, {})
    somatorio_integral = get_somatorio_integral("refeicao", solicitacao, {}, {})
    somatorio_programas_e_projetos = get_somatorio_programas_e_projetos(
        "refeicao", solicitacao, {}, {}
    )
    somatorio_solicitacoes_de_alimentacao = get_somatorio_solicitacoes_de_alimentacao(
        "refeicao", solicitacao
    )
    valores_somatorios_tabela = [
        somatorio_manha,
        somatorio_tarde,
        somatorio_integral,
        somatorio_programas_e_projetos,
        somatorio_solicitacoes_de_alimentacao,
    ]
    assert get_somatorio_total_tabela(valores_somatorios_tabela) == 450


def test_utils_build_tabela_somatorio_body(
    solicitacao_medicao_inicial_com_valores_repeticao,
):
    assert build_tabela_somatorio_body(
        solicitacao_medicao_inicial_com_valores_repeticao, {}, {}
    ) == [
        ["Lanche", 50, 50, 50, 50, 50, 250, 50, 50, 100],
        ["Refeição", 100, 100, 100, 100, 50, 450, 100, 100, 200],
        ["Kit Lanche", 50, 50, 50, 50, 50, 250, 50, 50, 100],
        ["Sobremesa", 100, 100, 100, 100, 50, 450, 100, 100, 200],
        ["Lanche Emergencial", 50, 50, 50, 50, 50, 250, 50, 50, 100],
    ]


def test_build_row_primeira_tabela(solicitacao_medicao_inicial_com_valores_repeticao):
    campos_categorias_primeira_tabela = [
        {
            "categoria": "Solicitação Alimentação",
            "campos": ["lanche_emergencial", "kit_lanche"],
        },
        {"categoria": "MANHA", "campos": ["lanche", "refeicao", "sobremesa"]},
        {"categoria": "TARDE", "campos": ["lanche", "refeicao", "sobremesa"]},
        {
            "categoria": "INTEGRAL",
            "campos": ["lanche_4h", "lanche", "refeicao", "sobremesa"],
        },
        {"categoria": "NOITE", "campos": ["lanche", "refeicao", "sobremesa"]},
    ]

    assert build_row_primeira_tabela(
        solicitacao_medicao_inicial_com_valores_repeticao,
        campos_categorias_primeira_tabela,
    ) == [
        solicitacao_medicao_inicial_com_valores_repeticao.escola.tipo_unidade,
        "123456",
        "EMEF TESTE",
        50,
        50,
        50,
        "-",
        "-",
        50,
        "-",
        "-",
        "-",
        50,
        "-",
        "-",
        50,
        "-",
        "-",
    ]
