from unittest import TestCase

import pytest
from django.core.management import call_command
from model_mommy import mommy

from sme_terceirizadas.perfil.models import Perfil, PerfisVinculados

from ....dados_comuns.constants import (
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_GESTAO_PRODUTO,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_PRODUTO
)


class CargaPerfisVinculadosCommandTest(TestCase):
    def call_command(self, *args, **kwargs):
        call_command(
            'carga_perfis_vinculados',
            *args,
            **kwargs,
        )

    def setUp(self) -> None:
        mommy.make(
            Perfil,
            nome=ADMINISTRADOR_DIETA_ESPECIAL,
        )
        mommy.make(
            Perfil,
            nome=ADMINISTRADOR_GESTAO_PRODUTO,
        )
        mommy.make(
            Perfil,
            nome=COORDENADOR_DIETA_ESPECIAL,
        )
        mommy.make(
            Perfil,
            nome=COORDENADOR_GESTAO_PRODUTO,
        )

    @pytest.mark.django_db(transaction=True)
    def test_command_carga(self) -> None:
        self.call_command()
        dieta = PerfisVinculados.objects.filter(perfil_master__nome=COORDENADOR_DIETA_ESPECIAL)[0]
        produto = PerfisVinculados.objects.filter(perfil_master__nome=COORDENADOR_GESTAO_PRODUTO)[0]
        assert dieta.perfis_subordinados.first().nome == ADMINISTRADOR_DIETA_ESPECIAL
        assert produto.perfis_subordinados.first().nome == ADMINISTRADOR_GESTAO_PRODUTO
