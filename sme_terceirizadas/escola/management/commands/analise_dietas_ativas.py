from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from utility.carga_dados.helper import excel_to_list_with_openpyxl

from sme_terceirizadas.escola.utils_analise_dietas_ativas import (
    escreve_xlsx_primeira_aba,
    gera_dict_codigo_aluno_por_codigo_escola,
    gera_dict_codigos_escolas,
    get_escolas_json,
    retorna_alunos_com_nascimento_diferente,
    retorna_alunos_com_nome_diferente,
    retorna_alunos_nao_matriculados_na_escola,
    retorna_cod_diagnostico_inexistentes,
    retorna_codigo_eol_escolas_nao_identificadas,
    retorna_dados_sigpae,
    retorna_protocolo_dieta_inexistentes
)

DATA = date.today().isoformat().replace('-', '_')
home = str(Path.home())
dict_codigos_escolas = {}
dict_codigo_aluno_por_codigo_escola = {}


def main(arquivo, arquivo_codigos_escolas):
    arquivo_saida = f'{home}/resultado_analise_dietas_ativas.xlsx'
    items = excel_to_list_with_openpyxl(arquivo, in_memory=False)
    escolas = get_escolas_json(f'{home}/escolas.json')

    # 1
    items_codigos_escolas = excel_to_list_with_openpyxl(arquivo_codigos_escolas, in_memory=False)
    gera_dict_codigos_escolas(items_codigos_escolas)
    retorna_codigo_eol_escolas_nao_identificadas(items, arquivo_saida)

    # 2
    # Usa items_codigos_escolas
    # Usa gera_dict_codigos_escolas
    gera_dict_codigo_aluno_por_codigo_escola(items)
    retorna_alunos_nao_matriculados_na_escola(items, escolas, arquivo_saida)

    # 3 - Retorna nome e data de nascimento que forem diferentes entre a planilha e o EOL.
    retorna_alunos_com_nome_diferente(items, escolas, arquivo_saida)
    retorna_alunos_com_nascimento_diferente(items, escolas, arquivo_saida)

    # 5
    # Usa items_codigos_escolas
    # Usa gera_dict_codigos_escolas
    retorna_dados_sigpae(items, arquivo_saida)

    # 6 Verificar os campos "CodDiagnostico" e "ProtocoloDieta"
    retorna_cod_diagnostico_inexistentes(items, arquivo_saida)
    retorna_protocolo_dieta_inexistentes(items, arquivo_saida)

    escreve_xlsx_primeira_aba(arquivo_saida)


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
        parser.add_argument(
            '--arquivo_codigos_escolas', '-ace',
            dest='arquivo_codigos_escolas',
            help='Informar caminho absoluto do arquivo xlsx.'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        arquivo_codigos_escolas = options['arquivo_codigos_escolas']
        main(arquivo, arquivo_codigos_escolas)
