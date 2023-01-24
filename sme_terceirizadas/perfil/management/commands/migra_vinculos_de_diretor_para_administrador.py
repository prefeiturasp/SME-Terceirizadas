import logging

from django.core.management import BaseCommand

from sme_terceirizadas.dados_comuns.constants import ADMINISTRADOR_UE, DIRETOR_UE
from sme_terceirizadas.perfil.models import Perfil, Vinculo

logger = logging.getLogger('sigpae.migra_vinculos_de_diretor_para_administrador')


class Command(BaseCommand):
    help = 'Migra usuários que possuam vinculo de DIRETOR para ADMINISTRADOR_UE'

    def handle(self, *args, **options):
        self.migra_vinculos()

    def migra_vinculos(self):
        adm_ue = Perfil.by_nome(ADMINISTRADOR_UE)
        Vinculo.objects.filter(perfil__nome__in=[DIRETOR_UE]).update(perfil=adm_ue)
