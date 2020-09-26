from sme_terceirizadas.escola.data.diretorias_regionais import data_diretorias_regionais
from sme_terceirizadas.escola.data.lotes import data_lotes
from sme_terceirizadas.escola.data.subprefeituras import data_subprefeituras
from sme_terceirizadas.escola.data.tipos_gestao import data_tipos_gestao
from sme_terceirizadas.escola.models import DiretoriaRegional
from sme_terceirizadas.escola.models import TipoGestao
from sme_terceirizadas.escola.models import Lote
from sme_terceirizadas.escola.models import Subprefeitura
from utility.carga_dados.helper import ja_existe
from utility.carga_dados.escola.helper import bcolors


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
            print(f'{bcolors.FAIL}Aviso: DiretoriaRegional: "{nome}" já existe!{bcolors.ENDC}')


def cria_lotes():
    pass


def cria_subprefeituras():
    pass


def cria_tipos_gestao():
    pass
