from django.db import connection

SQL_RELATORIO_QUANTITATIVO = """
    SELECT terceirizada_terceirizada.nome_fantasia nome_terceirizada,
       produto_homologacaodoproduto.status,
       count(*)
    FROM django_content_type,
         perfil_vinculo,
         perfil_usuario,
         produto_homologacaodoproduto,
         produto_produto,
         terceirizada_terceirizada
    WHERE perfil_vinculo.content_type_id = django_content_type.id
      AND terceirizada_terceirizada.id = object_id
      AND perfil_vinculo.usuario_id = perfil_usuario.id
      AND produto_produto.criado_por_id = perfil_usuario.id
      AND produto_homologacaodoproduto.produto_id = produto_produto.id
      AND django_content_type.app_label = 'terceirizada'
      AND django_content_type.model = 'terceirizada'
      {0}
    GROUP BY nome_terceirizada, status
    ORDER BY nome_terceirizada
"""

SQL_RELATORIO_QUANTITATIVO_POR_NOME = 'AND LOWER(terceirizada_terceirizada.nome_fantasia) LIKE %s'
SQL_RELATORIO_QUANTITATIVO_A_PARTIR_DE = 'AND produto_produto.criado_em >= %s'
SQL_RELATORIO_QUANTITATIVO_ATE = 'AND produto_produto.criado_em <= %s'


def obtem_dados_relatorio_quantitativo(form_data):  # noqa C901
    extra_where_clauses = []
    extra_arguments = []

    if form_data['nome_terceirizada'] != '':
        extra_where_clauses.append(SQL_RELATORIO_QUANTITATIVO_POR_NOME)
        extra_arguments.append('%{0}%'.format(form_data['nome_terceirizada'].lower()))
    if form_data['data_inicial'] is not None:
        extra_where_clauses.append(SQL_RELATORIO_QUANTITATIVO_A_PARTIR_DE)
        extra_arguments.append(form_data['data_inicial'].isoformat())
    if form_data['data_final'] is not None:
        extra_where_clauses.append(SQL_RELATORIO_QUANTITATIVO_ATE)
        extra_arguments.append(form_data['data_final'].isoformat())

    sql = SQL_RELATORIO_QUANTITATIVO.format(' '.join(extra_where_clauses))
    with connection.cursor() as cursor:
        cursor.execute(sql, extra_arguments)
        rows = cursor.fetchall()

    ultima_terceirizada = None
    lista_dados = []
    dados_terc_atual = {}

    for row in rows:
        if ultima_terceirizada is not None and row[0] != ultima_terceirizada:
            lista_dados.append(dados_terc_atual)
            ultima_terceirizada = None
        if ultima_terceirizada is None:
            dados_terc_atual = {
                'nome_terceirizada': row[0],
                'qtde_por_status': [{
                    'status': row[1],
                    'qtde': row[2]
                }]
            }
            ultima_terceirizada = row[0]
        elif row[0] == ultima_terceirizada:
            dados_terc_atual['qtde_por_status'].append({
                'status': row[1],
                'qtde': row[2]
            })

    if dados_terc_atual != {}:
        lista_dados.append(dados_terc_atual)

    retorno = {'results': lista_dados}

    if form_data['data_inicial'] is not None and form_data['data_final'] is not None:
        retorno['dias'] = (form_data['data_final'] - form_data['data_inicial']).days
    return retorno
