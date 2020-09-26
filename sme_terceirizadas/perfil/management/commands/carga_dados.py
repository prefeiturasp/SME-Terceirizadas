from django.core.management.base import BaseCommand
from utility.carga_dados.usuarios import cria_usuarios


class Command(BaseCommand):
    help = 'Importa dados iniciais no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write('Importando dados...')
        cria_usuarios()
