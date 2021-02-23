from django.core.management.base import BaseCommand

from sme_terceirizadas.escola.utils_analise_dietas_ativas import main


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
