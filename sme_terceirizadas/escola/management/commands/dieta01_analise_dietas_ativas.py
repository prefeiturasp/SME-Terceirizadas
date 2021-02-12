import openpyxl
from datetime import date
from django.core.management.base import BaseCommand
from utility.carga_dados.helper import excel_to_list_with_openpyxl, progressbar
from sme_terceirizadas.escola.models import Escola

DATA = date.today().isoformat().replace('-', '_')


def get_codigo_eol(valor):
    return valor.strip().zfill(6)


def escreve_xlsx(codigo_eol_escola_nao_existentes, arquivo_saida):
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('Código EOL das Escolas não identificadas no SIGPAE')
    ws['A1'] = 'codigo_eol_escola'
    for i, item in enumerate(progressbar(list(codigo_eol_escola_nao_existentes), 'Escrevendo...')):
        ws[f'A{i+2}'] = str(item)
    nome = arquivo_saida.split('.')
    wb.save(f'{nome[0]}_{DATA}.{nome[1]}')


def retorna_codigo_eol_escolas_nao_identificadas(items, arquivo_saida):
    cod_escola_unicos = set([get_codigo_eol(item['CodEscola']) for item in items])
    codigo_eol_sigpae_lista = Escola.objects.values_list('codigo_eol', flat=True)
    codigo_eol_escola_nao_existentes = cod_escola_unicos - set(codigo_eol_sigpae_lista)
    escreve_xlsx(codigo_eol_escola_nao_existentes, arquivo_saida)


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
        arquivo_saida = '/home/regis/Downloads/resultado_analise_dietas_ativas.xlsx'
        items = excel_to_list_with_openpyxl(arquivo, in_memory=False)
        retorna_codigo_eol_escolas_nao_identificadas(items, arquivo_saida)
