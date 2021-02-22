from django.core.management.base import BaseCommand

from sme_terceirizadas.escola.utils_escola import get_escolas


class Command(BaseCommand):
    help = """
    Lê uma planilha específica com Dietas Ativas a serem integradas no sistema.
    Pega todos os códigos EOL da escola na API do EOL.
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
        get_escolas(arquivo, arquivo_codigos_escolas, in_memory=False)
