from django.core.management.base import BaseCommand
from utility.carga_dados.helper import excel_to_list_with_openpyxl
from sme_terceirizadas.escola.models import Escola


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
        items = excel_to_list_with_openpyxl(arquivo, in_memory=False)
        cod_escola_unicos = set([item['CodEscola'] for item in items])
        codigo_eol_sigpae_lista = Escola.objects.values_list('codigo_eol', flat=True)
        codigo_eol_escola_nao_existentes = cod_escola_unicos - set(codigo_eol_sigpae_lista)
        print(len(codigo_eol_escola_nao_existentes))
