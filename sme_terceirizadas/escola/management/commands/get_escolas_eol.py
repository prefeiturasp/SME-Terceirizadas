import asyncio
import httpx
import openpyxl
import subprocess
import time
import timeit
from datetime import datetime, date
from pathlib import Path
from pprint import pprint
from time import sleep
from django.core.management.base import BaseCommand
from rest_framework import status

from utility.carga_dados.helper import excel_to_list_with_openpyxl, progressbar
from sme_terceirizadas.dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL


MDATA = datetime.now().strftime('%Y%m%d_%H%M%S')
DEFAULT_HEADERS = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
DATA = date.today().isoformat().replace('-', '_')
home = str(Path.home())
dict_codigos_escolas = {}
dict_codigo_aluno_por_codigo_escola = {}
arquivo = f'{home}/Downloads/banco_de_dietas_ativas_05.02.xlsx'
arquivo_codigos_escolas = f'{home}/Downloads/unidades_da_rede_28.01_.xlsx'


def get_codigo_eol_escola(valor):
    return valor.strip().zfill(6)


def get_codigo_eol_aluno(valor):
    return str(valor).strip().zfill(7)


def gera_dict_codigos_escolas(items_codigos_escolas):
    for item in items_codigos_escolas:
        dict_codigos_escolas[str(item['CÓDIGO UNIDADE'])] = str(item['CODIGO EOL'])


def grava_codescola_nao_existentes(valor):
    with open(f'{home}/codescola_nao_existentes.txt', 'a') as f:
        f.write(f"{valor}\n")


def gera_dict_codigo_aluno_por_codigo_escola(items):
    for item in items:
        try:
            codigo_eol_escola = dict_codigos_escolas[item['CodEscola']]
        except Exception as e:
            # Grava os CodEscola não existentes em unidades_da_rede_28.01_.xlsx
            grava_codescola_nao_existentes(item['CodEscola'])

        cod_eol_aluno = get_codigo_eol_aluno(item['CodEOLAluno'])
        dict_codigo_aluno_por_codigo_escola[cod_eol_aluno] = get_codigo_eol_escola(codigo_eol_escola)


def get_escolas_unicas(items):
    """
    A partir da planilha, pegar todas as escolas únicas "escolas_da_planilha"
    Retorna escolas únicas.
    """
    escolas = []
    for item in items:
        escolas.append(item['CodEscola'])
    return set(escolas)


class EOLException(Exception):
    pass


def escreve_escolas_json(texto):
    with open(f'{home}/escolas.json', 'a') as f:
        f.write(texto)


def ajustes_no_arquivo():
    # Troca aspas simples por aspas duplas (foi necessário dois replace).
    subprocess.run(f'sed -i "s/\'/?/g" {home}/escolas.json', shell=True)
    subprocess.run(f"sed -i 's/?/\"/g' {home}/escolas.json", shell=True)

    # Insere uma vírgula em todas as linhas exceto na última
    subprocess.run(f"sed -i '$ !s/$/,/' {home}/escolas.json", shell=True)

    # remove virgula da primeira linha
    subprocess.run(f"sed -i '1s/,//' {home}/escolas.json", shell=True)


async def get_informacoes_escola_turma_aluno(codigo_eol: str):
    headers = DEFAULT_HEADERS
    async with httpx.AsyncClient(headers=headers, timeout=None) as client:
        url = f'{DJANGO_EOL_API_URL}/escola_turma_aluno/{codigo_eol}'
        response = await client.get(url)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 0:
                raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
            print(len(results))

            escreve_escolas_json(f'"{codigo_eol}": {results}\n')

            return results
        else:
            with open(f'{home}/codigo_eol_erro_da_api_eol.txt', 'a') as f:
                f.write(f"{codigo_eol}\n")


async def main(escolas_da_planilha):
    task_list = []

    escreve_escolas_json('{\n')

    for i, escola in enumerate(escolas_da_planilha):
        try:
            codigo_eol_escola = get_codigo_eol_escola(dict_codigos_escolas[escola])
            task_list.append(get_informacoes_escola_turma_aluno(codigo_eol_escola))
        except Exception as e:
            # Grava os CodEscola não existentes em unidades_da_rede_28.01_.xlsx
            grava_codescola_nao_existentes(escola)

    await asyncio.gather(*task_list)

    ajustes_no_arquivo()
    escreve_escolas_json('}\n')


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_time = time.monotonic()

        items = excel_to_list_with_openpyxl(arquivo, in_memory=False)
        items_codigos_escolas = excel_to_list_with_openpyxl(arquivo_codigos_escolas, in_memory=False)

        gera_dict_codigos_escolas(items_codigos_escolas)
        gera_dict_codigo_aluno_por_codigo_escola(items)

        # A partir da planilha, pegar todas as escolas únicas "escolas_da_planilha"
        escolas_da_planilha = list(get_escolas_unicas(items))
        print('Escolas:', len(escolas_da_planilha))

        # Particiona os intervalos da lista para fazer apenas 100 requisições por vez.
        limit = 100  # 3
        # for i in range(0, 2 + 1, limit):
        for i in range(0, len(escolas_da_planilha) + 1, limit):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main(escolas_da_planilha[i:i+limit]))
            print('Waiting...')
            time.sleep(10)

        time_taken = round(time.monotonic() - start_time, 2)
        print(f"Time Taken:{time_taken}")
        # Remover
        with open('/tmp/tempo.txt', 'a') as f:
            f.write(f'{len(escolas_da_planilha)} escolas em {time_taken} s\n')
