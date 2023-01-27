import logging

from django.core.management import BaseCommand

from sme_terceirizadas.dados_comuns.constants import ADMINISTRADOR_EMPRESA, ADMINISTRADOR_UE, USUARIO_EMPRESA
from sme_terceirizadas.perfil.models import Perfil, Vinculo

logger = logging.getLogger('sigpae.atualiza_vinculos_de_perfis_removidos')


class Command(BaseCommand):
    help = 'Migra usuários que possuam vinculos de perfis extintos para novos perfis.'

    def handle(self, *args, **options):
        self.migra_vinculos_escola()
        self.migra_vinculos_empresa()
        self.migra_vinculos_empresa_usuario_terceirizada()

    def migra_vinculos_escola(self):
        adm_ue = Perfil.by_nome(ADMINISTRADOR_UE)
        Vinculo.objects.filter(perfil__nome__in=['DIRETOR',
                                                 'DIRETOR_CEI',
                                                 'DIRETOR_ABASTECIMENTO',
                                                 'COORDENADOR_ESCOLA',
                                                 'ADMINISTRADOR_ESCOLA',
                                                 'ADMINISTRADOR_UE_MISTA',
                                                 'ADMINISTRADOR_UE_DIRETA',
                                                 'ADMINISTRADOR_UE_PARCEIRA',
                                                 'ADMINISTRADOR_ESCOLA_ABASTECIMENTO']).update(perfil=adm_ue)

    def migra_vinculos_empresa(self):
        adm_empresa = Perfil.by_nome(ADMINISTRADOR_EMPRESA)
        Vinculo.objects.filter(
            perfil__nome__in=['NUTRI_ADMIN_RESPONSAVEL',
                              'ADMINISTRADOR_DISTRIBUIDORA',
                              'ADMINISTRADOR_FORNECEDOR']).update(perfil=adm_empresa)

    def migra_vinculos_empresa_usuario_terceirizada(self):
        usuario_empresa = Perfil.by_nome(USUARIO_EMPRESA)
        Vinculo.objects.filter(
            perfil__nome__in=['ADMINISTRADOR_TERCEIRIZADA']).update(perfil=usuario_empresa)
