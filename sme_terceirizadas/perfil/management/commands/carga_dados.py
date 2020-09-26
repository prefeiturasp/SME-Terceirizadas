from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Importa dados iniciais no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write('Importando dados...')
