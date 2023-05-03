import pytest

from sme_terceirizadas.medicao_inicial.utils import (
    build_dict_relacao_categorias_e_campos,
    build_headers_tabelas,
    build_tabelas_relatorio_medicao
)

pytestmark = pytest.mark.django_db


def test_utils_build_dict_relacao_categorias_e_campos(solicitacao_medicao_inicial_varios_valores):
    assert build_dict_relacao_categorias_e_campos(
        solicitacao_medicao_inicial_varios_valores.medicoes.get(periodo_escolar__nome='MANHA')) == {
        'ALIMENTAÇÃO': [
            'matriculados', 'total_refeicoes_pagamento', 'total_sobremesas_pagamento', 'lanche', 'lanche_emergencial',
            'refeicao', 'sobremesa'
        ],
        'DIETA ESPECIAL - TIPO A ENTERAL': [
            'aprovadas', 'lanche', 'lanche_emergencial', 'refeicao', 'sobremesa'
        ],
        'DIETA ESPECIAL - TIPO B': [
            'aprovadas', 'lanche', 'lanche_emergencial', 'refeicao', 'sobremesa'
        ]
    }


def test_utils_build_headers_tabelas(solicitacao_medicao_inicial_varios_valores):
    assert build_headers_tabelas(solicitacao_medicao_inicial_varios_valores) == [
        {
            'periodos': ['MANHA'],
            'categorias': ['ALIMENTAÇÃO', 'DIETA ESPECIAL - TIPO A ENTERAL'],
            'nomes_campos': [
                'matriculados', 'lanche', 'refeicao', 'lanche_emergencial', 'total_refeicoes_pagamento',
                'sobremesa', 'total_sobremesas_pagamento', 'aprovadas', 'lanche', 'refeicao',
                'lanche_emergencial', 'sobremesa'
            ],
            'len_periodos': [12],
            'len_categorias': [7, 5],
            'valores_campos': [],
            'ordem_periodos_grupos': [1, 1],
            'dias_letivos': []
        },
        {
            'periodos': ['MANHA', 'TARDE'],
            'categorias': ['DIETA ESPECIAL - TIPO B', 'ALIMENTAÇÃO'],
            'nomes_campos': [
                'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa', 'matriculados', 'lanche',
                'refeicao', 'lanche_emergencial', 'total_refeicoes_pagamento', 'sobremesa', 'total_sobremesas_pagamento'
            ],
            'len_periodos': [5, 7],
            'len_categorias': [5, 7],
            'valores_campos': [],
            'ordem_periodos_grupos': [1, 2],
            'dias_letivos': []
        },
        {
            'periodos': ['TARDE'],
            'categorias': ['DIETA ESPECIAL - TIPO A ENTERAL', 'DIETA ESPECIAL - TIPO B'],
            'nomes_campos': [
                'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa', 'aprovadas', 'lanche',
                'refeicao', 'lanche_emergencial', 'sobremesa'
            ],
            'len_periodos': [10],
            'len_categorias': [5, 5],
            'valores_campos': [],
            'ordem_periodos_grupos': [2, 2],
            'dias_letivos': []
        }
    ]


def test_build_tabelas_relatorio_medicao(solicitacao_medicao_inicial_varios_valores):
    assert build_tabelas_relatorio_medicao(solicitacao_medicao_inicial_varios_valores) == [
        {
            'periodos': ['MANHA'],
            'categorias': ['ALIMENTAÇÃO', 'DIETA ESPECIAL - TIPO A ENTERAL'],
            'nomes_campos': [
                'matriculados', 'lanche', 'refeicao', 'lanche_emergencial', 'total_refeicoes_pagamento', 'sobremesa',
                'total_sobremesas_pagamento', 'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa'
            ],
            'len_periodos': [12],
            'len_categorias': [7, 5],
            'valores_campos': [
                [1, '0', '10', '10', '10', '0', '10', '0', '0', '10', '10', '10', '10'],
                [2, '0', '10', '10', '10', '0', '10', '0', '0', '10', '10', '10', '10'],
                [3, '0', '10', '10', '10', '0', '10', '0', '0', '10', '10', '10', '10'],
                [4, '0', '10', '10', '10', '0', '10', '0', '0', '10', '10', '10', '10'],
                [5, '0', '10', '10', '10', '0', '10', '0', '0', '10', '10', '10', '10'],
                [6, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [7, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [8, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [9, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [10, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [11, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [12, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [13, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [14, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [15, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [16, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [17, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [18, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [19, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [20, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [21, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [22, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [23, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [24, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [25, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [26, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [27, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [28, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [29, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [30, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [31, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                ['Total', '-', 50, 50, 50, 0, 50, 0, '-', 50, 50, 50, 50]],
            'ordem_periodos_grupos': [1, 1],
            'dias_letivos': [
                False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False, False, False
            ]
        },
        {
            'periodos': ['MANHA', 'TARDE'],
            'categorias': ['DIETA ESPECIAL - TIPO B', 'ALIMENTAÇÃO'],
            'nomes_campos': [
                'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa', 'matriculados',
                'lanche', 'refeicao', 'lanche_emergencial', 'total_refeicoes_pagamento', 'sobremesa',
                'total_sobremesas_pagamento'
            ],
            'len_periodos': [5, 7],
            'len_categorias': [5, 7],
            'valores_campos': [
                [1, '0', '10', '10', '10', '10', '0', '10', '10', '10', '0', '10', '0'],
                [2, '0', '10', '10', '10', '10', '0', '10', '10', '10', '0', '10', '0'],
                [3, '0', '10', '10', '10', '10', '0', '10', '10', '10', '0', '10', '0'],
                [4, '0', '10', '10', '10', '10', '0', '10', '10', '10', '0', '10', '0'],
                [5, '0', '10', '10', '10', '10', '0', '10', '10', '10', '0', '10', '0'],
                [6, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [7, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [8, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [9, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [10, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [11, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [12, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [13, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [14, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [15, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [16, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [17, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [18, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [19, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [20, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [21, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [22, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [23, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [24, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [25, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [26, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [27, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [28, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [29, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [30, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [31, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                ['Total', '-', 50, 50, 50, 50, '-', 50, 50, 50, 0, 50, 0]],
            'ordem_periodos_grupos': [1, 2],
            'dias_letivos': [
                False, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False
            ]
        },
        {
            'periodos': ['TARDE'],
            'categorias': ['DIETA ESPECIAL - TIPO A ENTERAL', 'DIETA ESPECIAL - TIPO B'],
            'nomes_campos': [
                'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa',
                'aprovadas', 'lanche', 'refeicao', 'lanche_emergencial', 'sobremesa'
            ],
            'len_periodos': [10],
            'len_categorias': [5, 5],
            'valores_campos': [
                [1, '0', '10', '10', '10', '10', '0', '10', '10', '10', '10'],
                [2, '0', '10', '10', '10', '10', '0', '10', '10', '10', '10'],
                [3, '0', '10', '10', '10', '10', '0', '10', '10', '10', '10'],
                [4, '0', '10', '10', '10', '10', '0', '10', '10', '10', '10'],
                [5, '0', '10', '10', '10', '10', '0', '10', '10', '10', '10'],
                [6, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [7, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [8, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [9, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [10, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [11, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [12, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [13, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [14, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [15, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [16, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [17, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [18, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [19, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [20, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [21, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [22, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [23, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [24, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [25, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [26, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [27, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [28, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [29, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [30, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                [31, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                ['Total', '-', 50, 50, 50, 50, '-', 50, 50, 50, 50]
            ],
            'ordem_periodos_grupos': [2, 2],
            'dias_letivos': [
                False, False, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False
            ]
        }
    ]
