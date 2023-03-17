import logging

from django.core.management import BaseCommand

from sme_terceirizadas.dados_comuns.constants import COGESTOR_DRE
from sme_terceirizadas.perfil.models import Perfil, Vinculo

logger = logging.getLogger('sigpae.atualiza_vinculos_de_perfis_removidos')


class Command(BaseCommand):
    help = 'Migra usuários que possuam vinculos de perfis extintos para novos perfis.'

    def handle(self, *args, **options):
        self.unificar_perfis_dre()

    def unificar_perfis_dre(self):
        Perfil.objects.filter(nome__iexact='COGESTOR_DRE').update(nome=COGESTOR_DRE)
        perfil = Perfil.objects.get(nome__iexact=COGESTOR_DRE)
        Vinculo.objects.filter(perfil__nome__in=['ADMINISTRADOR_DRE', 'SUPLENTE']).update(perfil=perfil)
