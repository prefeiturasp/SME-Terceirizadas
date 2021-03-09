from django.conf import settings
from django.core.management.base import BaseCommand

from sme_terceirizadas.dieta_especial.models import SolicitacaoDietaEspecial


def deletar_dieta(dieta_uuid):
    dieta = SolicitacaoDietaEspecial.objects.get(uuid__startswith=dieta_uuid)
    dieta.delete()


class Command(BaseCommand):
    help = """
    Deleta uma Dieta Especial, informando o uuid da Dieta.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--uuid', '-u',
            dest='uuid',
            help='Informar uuid (5 primeiros dígitos) da dieta.'
        )

    def handle(self, *args, **options):
        if settings.DEBUG:
            uuid = options['uuid']
            deletar_dieta(uuid)
            self.stdout.write(f'Dieta Deletada.')
        else:
            self.stdout.write(f'Usar somente em Dev.')
