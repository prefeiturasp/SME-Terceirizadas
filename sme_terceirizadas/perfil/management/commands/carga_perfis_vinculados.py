from django.core.management.base import BaseCommand

from ....dados_comuns.constants import (
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_GESTAO_PRODUTO,
    ADMINISTRADOR_SUPERVISAO_NUTRICAO,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_PRODUTO,
    COORDENADOR_SUPERVISAO_NUTRICAO
)
from ...models import Perfil, PerfisVinculados


class Command(BaseCommand):
    help = """Cria os registros na tabela de Perfis Vinculados indicando as hierarquias entre perfis do sistema."""

    def handle(self, *args, **options):
        self.cria_perfil_vinculado(COORDENADOR_GESTAO_PRODUTO, [ADMINISTRADOR_GESTAO_PRODUTO])
        self.cria_perfil_vinculado(COORDENADOR_DIETA_ESPECIAL, [ADMINISTRADOR_DIETA_ESPECIAL])
        self.cria_perfil_vinculado(COORDENADOR_SUPERVISAO_NUTRICAO, [ADMINISTRADOR_SUPERVISAO_NUTRICAO])

    def cria_perfil_vinculado(self, master, subordinados):
        perfil = Perfil.objects.get(nome=master)
        perfil_vinculado = PerfisVinculados.objects.filter(perfil_master=perfil)
        if perfil_vinculado.count() == 0:
            instance = PerfisVinculados.objects.create(
                perfil_master=perfil,
            )
            subordinados = Perfil.objects.filter(nome__in=subordinados)
            instance.perfis_subordinados.add(*subordinados)
