import json
from unittest import TestCase
from unittest.mock import patch

import pytest
from django.core.management import call_command
from freezegun.api import freeze_time

from sme_sigpae_api.escola.fixtures.factories.escola_factory import (
    EscolaFactory,
    PeriodoEscolarFactory,
)
from sme_sigpae_api.escola.models import Aluno


class AtualizaAlunosEscolasCommandTest(TestCase):
    def call_command(self, *args, **kwargs):
        call_command(
            "atualiza_alunos_escolas",
            *args,
            **kwargs,
        )

    def set_up_periodos_escolares(self):
        PeriodoEscolarFactory.create(nome="MANHA", tipo_turno=1)
        PeriodoEscolarFactory.create(nome="INTERMEDIARIO", tipo_turno=2)
        PeriodoEscolarFactory.create(nome="TARDE", tipo_turno=3)
        PeriodoEscolarFactory.create(nome="VESPERTINO", tipo_turno=4)
        PeriodoEscolarFactory.create(nome="NOITE", tipo_turno=5)
        PeriodoEscolarFactory.create(nome="INTEGRAL", tipo_turno=6)

    def setUp(self) -> None:
        self.set_up_periodos_escolares()
        self.escola = EscolaFactory.create(codigo_eol="000086")

        with open(
            "sme_sigpae_api/escola/__tests__/commands/mocks/mock_ue_000086_dados_alunos_2024.json",
            "r",
        ) as file:
            self.mocked_response_dados_alunos = json.load(file)

        with open(
            "sme_sigpae_api/escola/__tests__/commands/mocks/mock_ue_000086_dados_alunos_2024.json",
            "r",
        ) as file:
            self.mocked_response_dados_alunos_prox_ano = json.load(file)

    @freeze_time("2024-12-12")
    @patch(
        "sme_sigpae_api.escola.management.commands.atualiza_alunos_escolas.Command._obtem_alunos_escola"
    )
    @pytest.mark.django_db(transaction=True)
    def test_command_atualiza_alunos_escolas_d_menos_2(
        self, mock_obtem_alunos_escola
    ) -> None:
        mock_obtem_alunos_escola.side_effect = [
            self.mocked_response_dados_alunos,
            self.mocked_response_dados_alunos_prox_ano,
        ]
        self.call_command()
        assert Aluno.objects.count() == 288

        aluno_davi = Aluno.objects.get(nome="DAVI LUCAS THOMAZ NASCIMENTO")
        assert aluno_davi.nao_matriculado is False
        assert aluno_davi.escola == self.escola

        assert Aluno.objects.filter(nome="ZOE MOURA VIANA CARDOSO").exists() is False

    @freeze_time("2025-01-01")
    @patch(
        "sme_sigpae_api.escola.management.commands.atualiza_alunos_escolas.Command._obtem_alunos_escola"
    )
    @pytest.mark.django_db(transaction=True)
    def test_command_atualiza_alunos_escolas_d_menos_1(
        self, mock_obtem_alunos_escola
    ) -> None:
        mock_obtem_alunos_escola.side_effect = [
            self.mocked_response_dados_alunos,
            self.mocked_response_dados_alunos_prox_ano,
        ]
        self.call_command()
        assert Aluno.objects.count() == 288

        aluno_davi = Aluno.objects.get(nome="DAVI LUCAS THOMAZ NASCIMENTO")
        assert aluno_davi.nao_matriculado is False
        assert aluno_davi.escola == self.escola

        assert Aluno.objects.filter(nome="ZOE MOURA VIANA CARDOSO").exists() is False
