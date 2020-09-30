import environ
from django.db.models import Q
from utility.carga_dados.escola.helper import bcolors, email_valido, maiuscula, normaliza_nome, somente_digitos
from utility.carga_dados.helper import adiciona_m2m_items, csv_to_list, get_modelo, ja_existe, le_dados, progressbar

from sme_terceirizadas.dados_comuns.models import Contato
from sme_terceirizadas.escola.data.diretorias_regionais import data_diretorias_regionais  # noqa
from sme_terceirizadas.escola.data.lotes import data_lotes
from sme_terceirizadas.escola.data.subprefeituras import data_subprefeituras
from sme_terceirizadas.escola.data.tipos_gestao import data_tipos_gestao
from sme_terceirizadas.escola.models import (
    DiretoriaRegional,
    Escola,
    Lote,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)
from sme_terceirizadas.terceirizada.data.terceirizadas import data_terceirizadas  # noqa
from sme_terceirizadas.terceirizada.models import Terceirizada

ROOT_DIR = environ.Path(__file__) - 1


def cria_diretorias_regionais():
    for item in progressbar(data_diretorias_regionais, 'Diretoria Regional'):
        obj = DiretoriaRegional.objects.filter(codigo_eol=item['codigo_eol']).first()  # noqa
        if not obj:
            DiretoriaRegional.objects.create(
                nome=item['nome'],
                iniciais=item['iniciais'],
                codigo_eol=item['codigo_eol'],
            )
        else:
            nome = item['nome']
            print(f'{bcolors.FAIL}Aviso: DiretoriaRegional: "{nome}" já existe!{bcolors.ENDC}')  # noqa


def cria_lotes():
    # Possui FK.
    # Monta o dicionário direto da lista de items.
    dict_tipo_gestao = le_dados(data_tipos_gestao, 'nome')
    dict_dre = le_dados(data_diretorias_regionais, 'codigo_eol')
    dict_terceirizada = le_dados(data_terceirizadas, 'cnpj')
    for item in progressbar(data_lotes, 'Lote'):
        tipo_gestao = get_modelo(
            modelo=TipoGestao,
            modelo_id=item.get('tipo_gestao'),
            dicionario=dict_tipo_gestao,
            campo_unico='nome'
        )
        diretoria_regional = get_modelo(
            modelo=DiretoriaRegional,
            modelo_id=item.get('diretoria_regional'),
            dicionario=dict_dre,
            campo_unico='codigo_eol'
        )
        terceirizada = get_modelo(
            modelo=Terceirizada,
            modelo_id=item.get('terceirizada'),
            dicionario=dict_terceirizada,
            campo_unico='cnpj'
        )

        data = dict(
            nome=item.get('nome'),
            iniciais=item.get('iniciais'),
            tipo_gestao=tipo_gestao,
            diretoria_regional=diretoria_regional,
            terceirizada=terceirizada,
        )
        _, created = Lote.objects.get_or_create(**data)
        if not created:
            ja_existe('Lote', item['nome'])


def cria_subprefeituras():
    # Possui FK e M2M
    dict_lote = le_dados(data_lotes, 'iniciais')
    dict_dre = le_dados(data_diretorias_regionais, 'codigo_eol')
    for item in progressbar(data_subprefeituras, 'Subprefeitura'):
        # Não tem lote nos dados originais.
        lote = get_modelo(
            modelo=Lote,
            modelo_id=item.get('lote'),
            dicionario=dict_lote,
            campo_unico='iniciais'
        )
        subprefeitura, created = Subprefeitura.objects.get_or_create(
            nome=item['nome'],
            lote=lote
        )
        if not created:
            ja_existe('Subprefeitura', item['nome'])

        adiciona_m2m_items(
            campo_m2m=subprefeitura.diretoria_regional,
            dicionario_m2m=item.get('diretoria_regional'),
            modelo=DiretoriaRegional,
            dicionario=dict_dre,
            campo_unico='codigo_eol'
        )


def cria_tipos_gestao():
    for item in progressbar(data_tipos_gestao, 'Tipo Gestao'):
        _, created = TipoGestao.objects.get_or_create(nome=item['nome'])
        if not created:
            ja_existe('TipoGestao', item['nome'])


def cria_tipo_unidade_escolar(arquivo):
    # Pega somente a coluna 'TIPO DE U.E'
    iniciais = 'TIPO DE U.E'
    arquivo = f'{ROOT_DIR}/{arquivo}'
    items = csv_to_list(arquivo)
    items_iniciais = [item[iniciais] for item in items]

    # Procura por todos os itens repetidos no banco,
    # e retorna uma lista de iniciais...
    tipo_unidade_escolares = TipoUnidadeEscolar.objects\
        .filter(iniciais__in=items_iniciais)\
        .values_list('iniciais', flat=True)

    # E insere somente os itens faltantes.
    itens_faltantes = set(items_iniciais) - set(tipo_unidade_escolares)
    if itens_faltantes:
        for iniciais in progressbar(itens_faltantes, 'Tipo Unidade Escolar'):
            TipoUnidadeEscolar.objects.create(iniciais=iniciais)


def cria_contatos_escola(arquivo):
    arquivo = f'{ROOT_DIR}/{arquivo}'
    items = csv_to_list(arquivo)

    for item in progressbar(items, 'Contatos Escola'):
        _email = item.get('E-MAIL').strip().lower() or ''
        email = _email if email_valido(_email) else ''

        telefone1 = somente_digitos(item.get('TELEFONE'))
        if 8 < len(telefone1) > 10:
            telefone1 = None
        telefone2 = somente_digitos(item.get('TELEFONE2'))
        if 8 < len(telefone2) > 10:
            telefone2 = None

        if telefone1 or telefone2 or email:
            Contato.objects.get_or_create(
                telefone=telefone1,
                telefone2=telefone2,
                email=email,
            )


def padroniza_dados(items):
    # Tudo Maiusculo + strip
    campos_maiusculos = (
        'EOL',
        'TIPO DE U.E',
        'NOME',
        'DRE',
        'SIGLA/LOTE',
        'ENDEREÇO',
        'Nº',
        'BAIRRO',
        'CEP',
        'EMPRESA',
        'COD. CODAE',
    )
    for item in items:
        for campo in campos_maiusculos:
            item[campo] = maiuscula(item[campo])

    # Tamanho de 6 digitos (zeros a esquerda).
    campos_6_digitos = ('EOL',)
    for item in items:
        for campo in campos_6_digitos:
            item[campo] = item[campo].zfill(6)

    # Normaliza nome.
    campos_normaliza_nomes = (
        'TIPO DE U.E',
        'DRE',
        'ENDEREÇO',
        'BAIRRO',
    )
    for item in items:
        for campo in campos_normaliza_nomes:
            item[campo] = normaliza_nome(item[campo])

    # Somente digitos
    campos_somente_digitos = (
        'CEP',
    )
    for item in items:
        for campo in campos_somente_digitos:
            item[campo] = somente_digitos(item[campo])

    return items


def cria_escola(arquivo, legenda):
    lista_auxiliar = []

    arquivo = f'{ROOT_DIR}/{arquivo}'
    items = csv_to_list(arquivo)

    # Padroniza os dados
    items = padroniza_dados(items)

    items_codigo_eol = [item['EOL'] for item in items]

    # Procura por todos os itens repetidos no banco,
    # e retorna uma lista de codigo_eol...
    escolas = Escola.objects\
        .filter(codigo_eol__in=items_codigo_eol)\
        .values_list('codigo_eol', flat=True)

    # E insere somente os itens faltantes.
    escolas_faltantes = [item for item in items if item['EOL'] not in escolas]
    if escolas_faltantes:
        for item in progressbar(escolas_faltantes, legenda):  # noqa
            dre_nome = item.get('DRE')
            tipo_ue_iniciais = item.get('TIPO DE U.E')
            lote_sigla = item.get('SIGLA/LOTE')
            email = item.get('E-MAIL').strip().lower() or ''
            telefone1 = somente_digitos(item.get('TELEFONE'))
            telefone2 = somente_digitos(item.get('TELEFONE2'))

            dre_obj, created_dre = DiretoriaRegional.objects.get_or_create(nome=dre_nome)  # noqa
            tipo_ue_obj, created_ue = TipoUnidadeEscolar.objects.get_or_create(iniciais=tipo_ue_iniciais)  # noqa
            tipo_gestao = TipoGestao.objects.get(nome='TERC TOTAL')
            lote_obj = Lote.objects.filter(iniciais=lote_sigla).first() or None
            if telefone1 or telefone2 or email:
                contato_obj = Contato.objects.filter(
                    Q(telefone=telefone1) |
                    Q(telefone2=telefone2) |
                    Q(email=email)
                ).first()

            tipo_ue = item.get('TIPO DE U.E')
            nome = item.get('NOME')
            # Instancia o objeto Escola.
            data = dict(
                nome=f'{tipo_ue} {nome}',
                codigo_eol=item.get('EOL'),
                diretoria_regional=dre_obj,
                tipo_unidade=tipo_ue_obj,
                tipo_gestao=tipo_gestao,
            )
            if lote_obj:
                data['lote'] = lote_obj
            if contato_obj:
                data['contato'] = contato_obj

            escola_obj = Escola(**data)
            lista_auxiliar.append(escola_obj)

        Escola.objects.bulk_create(lista_auxiliar)
