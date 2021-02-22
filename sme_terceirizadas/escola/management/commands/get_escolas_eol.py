from django.core.management.base import BaseCommand
from sme_terceirizadas.escola.utils_escola import get_escolas


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_escolas()
