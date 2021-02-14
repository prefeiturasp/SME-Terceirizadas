import openpyxl
import timeit
from datetime import date
from time import sleep
from pathlib import Path
from django.core.management.base import BaseCommand
from utility.carga_dados.helper import excel_to_list_with_openpyxl, progressbar
from sme_terceirizadas.escola.models import Escola
from sme_terceirizadas.eol_servico.utils import EOLService

DATA = date.today().isoformat().replace('-', '_')
home = str(Path.home())
dict_codigos_escolas = {}
dict_codigo_aluno_por_codigo_escola = {}


def get_codigo_eol_escola(valor):
    return valor.strip().zfill(6)


def get_codigo_eol_aluno(valor):
    return str(valor).strip().zfill(7)


def gera_dict_codigos_escolas(items_codigos_escolas):
    for item in items_codigos_escolas:
        dict_codigos_escolas[str(item['CÓDIGO UNIDADE'])] = str(item['CODIGO EOL'])


def gera_dict_codigo_aluno_por_codigo_escola(items):
    for item in items:
        codigo_eol_escola = dict_codigos_escolas[item['CodEscola']]
        cod_eol_aluno = get_codigo_eol_aluno(item['CodEOLAluno'])
        dict_codigo_aluno_por_codigo_escola[cod_eol_aluno] = get_codigo_eol_escola(codigo_eol_escola)


def get_escolas_unicas(items):
    # A partir da planilha, pegar todas as escolas únicas "escolas_da_planilha"
    escolas = []
    for item in items:
        escolas.append(item['CodEscola'])
    return set(escolas)


def escreve_xlsx(codigo_eol_escola_nao_existentes, arquivo_saida):
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('Código EOL das Escolas não identificadas no SIGPAE')
    ws['A1'] = 'codigo_eol_escola'
    for i, item in enumerate(progressbar(list(codigo_eol_escola_nao_existentes), 'Escrevendo...')):
        ws[f'A{i+2}'] = str(item)
    nome = arquivo_saida.split('.')
    wb.save(f'{nome[0]}_{DATA}.{nome[1]}')


def escreve_xlsx_alunos_nao_matriculados_na_escola(alunos_nao_matriculados_na_escola_lista, arquivo_saida):
    nome_ = arquivo_saida.split('.')
    nome = f'{nome_[0]}_{DATA}.{nome_[1]}'
    wb = openpyxl.load_workbook(nome)
    ws = wb.create_sheet('Código EOL dos Alunos não matriculados na escola')
    ws['A1'] = 'codigo_eol_aluno'
    ws['B1'] = 'nome_aluno'
    ws['C1'] = 'codigo_eol_escola'
    for i, item in enumerate(progressbar(list(alunos_nao_matriculados_na_escola_lista), 'Escrevendo...')):
        ws[f'A{i+2}'] = str(item[0])
        ws[f'B{i+2}'] = str(item[1])
        ws[f'C{i+2}'] = str(item[2])
    nome = arquivo_saida.split('.')
    wb.save(f'{nome[0]}_{DATA}.{nome[1]}')


def retorna_codigo_eol_escolas_nao_identificadas(items, arquivo_saida):
    cod_escola_unicos = set([get_codigo_eol_escola(item['CodEscola']) for item in items])
    codigo_eol_sigpae_lista = Escola.objects.values_list('codigo_eol', flat=True)
    codigo_eol_escola_nao_existentes = cod_escola_unicos - set(codigo_eol_sigpae_lista)
    escreve_xlsx(codigo_eol_escola_nao_existentes, arquivo_saida)


def retorna_Alunos_nao_matriculados_na_escola(escolas_da_planilha, items, arquivo_saida):
    # Percorrendo "escolas_da_planilha", a partir da planilha pegar todos os alunos de cada escola do iterador.
    tic = timeit.default_timer()

    alunos_nao_matriculados_na_escola_lista = []
    for i, escola in enumerate(list(escolas_da_planilha)[:5]):
        print(i, 'Lendo API do EOL...')
        if i % 4 == 0:
            sleep(2)
        # Pegar os alunos de cada escola do iterador.
        # Retorna uma tupla com CodEOLAluno e NomeAluno
        alunos_da_planilha_por_escola_lista = [
            (get_codigo_eol_aluno(item['CodEOLAluno']), item['NomeAluno'])
            for item in items if item['CodEscola'] == escola
        ]
        print('Alunos', i, escola)
        print(i, 'alunos_da_planilha_por_escola_lista', alunos_da_planilha_por_escola_lista)
        # Pegar todos os alunos por escola na API usando a função get_informacoes_escola_turma_aluno
        codigo_eol_escola = get_codigo_eol_escola(dict_codigos_escolas[escola])
        print('codigo_eol_escola', codigo_eol_escola)
        alunos_da_api_por_escola_lista = EOLService.get_informacoes_escola_turma_aluno(codigo_eol_escola)
        for cod_aluno, nome_aluno in alunos_da_planilha_por_escola_lista:
            pertence = any(
                get_codigo_eol_aluno(aluno['cd_aluno']) == cod_aluno
                for aluno in alunos_da_api_por_escola_lista
            )
            if not pertence:
                print(f'>>> Aluno {cod_aluno} - {nome_aluno} não pertence a escola {codigo_eol_escola}')
                alunos_nao_matriculados_na_escola_lista.append((cod_aluno, nome_aluno, codigo_eol_escola))
                print()

    if alunos_nao_matriculados_na_escola_lista:
        escreve_xlsx_alunos_nao_matriculados_na_escola(alunos_nao_matriculados_na_escola_lista, arquivo_saida)

    toc = timeit.default_timer()
    print('Time', round(toc - tic, 2))


class Command(BaseCommand):
    help = """
    Lê uma planilha específica com Dietas Ativas a serem integradas no sistema.
    Valida se o código EOL da unidade educacional da planilha Excel existe na base do SIGPAE.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo', '-a',
            dest='arquivo',
            help='Informar caminho absoluto do arquivo xlsx.'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        arquivo_codigos_escolas = f'{home}/Downloads/unidades_da_rede_28.01_.xlsx'
        arquivo_saida = f'{home}/Downloads/resultado_analise_dietas_ativas.xlsx'
        items = excel_to_list_with_openpyxl(arquivo, in_memory=False)
        # 1
        retorna_codigo_eol_escolas_nao_identificadas(items, arquivo_saida)

        # 2
        items_codigos_escolas = excel_to_list_with_openpyxl(arquivo_codigos_escolas, in_memory=False)

        gera_dict_codigos_escolas(items_codigos_escolas)
        gera_dict_codigo_aluno_por_codigo_escola(items)

        # A partir da planilha, pegar todas as escolas únicas "escolas_da_planilha"
        escolas_da_planilha = get_escolas_unicas(items)

        # Percorrendo "escolas_da_planilha", a partir da planilha pegar todos os alunos de cada escola do iterador.
        retorna_Alunos_nao_matriculados_na_escola(escolas_da_planilha, items, arquivo_saida)
