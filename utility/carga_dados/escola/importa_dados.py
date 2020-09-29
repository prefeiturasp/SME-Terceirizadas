from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import adiciona_m2m_items, get_modelo, ja_existe, le_dados, progressbar

from sme_terceirizadas.escola.data.diretorias_regionais import data_diretorias_regionais  # noqa
from sme_terceirizadas.escola.data.lotes import data_lotes
from sme_terceirizadas.escola.data.subprefeituras import data_subprefeituras
from sme_terceirizadas.escola.data.tipos_gestao import data_tipos_gestao
from sme_terceirizadas.escola.models import DiretoriaRegional, Lote, Subprefeitura, TipoGestao
from sme_terceirizadas.terceirizada.data.terceirizadas import data_terceirizadas  # noqa
from sme_terceirizadas.terceirizada.models import Terceirizada


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
