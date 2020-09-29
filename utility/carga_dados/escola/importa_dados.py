from sme_terceirizadas.escola.data.diretorias_regionais import data_diretorias_regionais  # noqa
from sme_terceirizadas.escola.data.lotes import data_lotes
from sme_terceirizadas.escola.data.subprefeituras import data_subprefeituras
from sme_terceirizadas.escola.data.tipos_gestao import data_tipos_gestao
from sme_terceirizadas.escola.models import DiretoriaRegional
from sme_terceirizadas.escola.models import Lote
from sme_terceirizadas.escola.models import Subprefeitura
from sme_terceirizadas.escola.models import TipoGestao
from sme_terceirizadas.terceirizada.data.terceirizadas import data_terceirizadas  # noqa
from sme_terceirizadas.terceirizada.models import Terceirizada
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import get_modelo
from utility.carga_dados.helper import ja_existe
from utility.carga_dados.helper import le_dados


def cria_diretorias_regionais():
    for item in data_diretorias_regionais:
        obj = DiretoriaRegional.objects.filter(
            codigo_eol=item['codigo_eol']).first()
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
    # Monta o dicionário direto da lista de items.
    dict_tipo_gestao = le_dados(data_tipos_gestao, 'nome')
    dict_dre = le_dados(data_diretorias_regionais, 'codigo_eol')
    dict_terceirizada = le_dados(data_terceirizadas, 'cnpj')
    for item in data_lotes:
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
    pass


def cria_tipos_gestao():
    for item in data_tipos_gestao:
        _, created = TipoGestao.objects.get_or_create(nome=item['nome'])
        if not created:
            ja_existe('TipoGestao', item['nome'])
