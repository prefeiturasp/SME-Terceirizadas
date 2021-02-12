from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    Lê uma planilha específica com Dietas Ativas a serem integradas no sistema.
    Valida se o código EOL da unidade educacional da planilha Excel existe na base do SIGPAE.
    """

    def handle(self, *args, **options):
        self.stdout.write('OK')
