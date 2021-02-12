from django.core.management.base import BaseCommand
from utility.carga_dados.helper import excel_to_list_with_openpyxl


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
        self.stdout.write(len(items))
