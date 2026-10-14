from unittest.mock import patch

import pytest
from model_bakery import baker

from src.medicao_inicial.models import GrupoMedicao
from src.medicao_inicial.validators import (
    validate_medicao_cemei_cei,
    validate_medicao_cemei_emei,
    validate_medicao_cemei_programas_e_projetos,
)

pytestmark = pytest.mark.django_db

MSG_ERRO_PERIODOS_ZERADOS = (
    "Avaliar lançamentos de dias sem frequencia nos demais períodos."
)


def _cria_solicitacao(escola):
    return baker.make(
        "SolicitacaoMedicaoInicial",
        escola=escola,
        mes="01",
        ano="2026",
    )


def _cria_medicao_com_grupo(solicitacao, nome_grupo):
    grupo = baker.make("GrupoMedicao", nome=nome_grupo)
    return baker.make(
        "Medicao",
        solicitacao_medicao_inicial=solicitacao,
        grupo=grupo,
    )


def _cria_medicao_com_periodo(solicitacao, nome_periodo):
    periodo = baker.make("PeriodoEscolar", nome=nome_periodo)
    return baker.make(
        "Medicao",
        solicitacao_medicao_inicial=solicitacao,
        periodo_escolar=periodo,
    )


class TestValidateMedicaoCemeiCei:

    def test_valida_apenas_periodo_integral_e_parcial(
        self, escola_cemei, categoria_medicao
    ):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_periodo(solicitacao, "INTEGRAL")
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_MANHA)

        with patch(
            "src.medicao_inicial.validators._validate_medicao_cei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_cei(solicitacao, [])

        assert mock_validate.call_count == 1

    def test_nao_processa_quando_nao_ha_periodo_integral_ou_parcial(
        self, escola_cemei, categoria_medicao
    ):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_MANHA)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_TARDE)

        with patch(
            "src.medicao_inicial.validators._validate_medicao_cei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_cei(solicitacao, [])

        assert mock_validate.call_count == 0


class TestValidateMedicaoCemeiProgramasEProjetos:

    def test_valida_apenas_grupo_programas_e_projetos(self, escola_cemei):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.PROGRAMAS_E_PROJETOS)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_MANHA)

        with patch(
            "src.medicao_inicial.validators._validate_solicitacoes_programas_e_projetos_emei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_programas_e_projetos(solicitacao, [])

        assert mock_validate.call_count == 1

    def test_nao_processa_quando_nao_ha_grupo_programas_e_projetos(self, escola_cemei):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_MANHA)

        with patch(
            "src.medicao_inicial.validators._validate_solicitacoes_programas_e_projetos_emei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_programas_e_projetos(solicitacao, [])

        assert mock_validate.call_count == 0

    def test_gera_erro_quando_periodos_zerados(
        self,
        solicitacao_medicao_finaliza_programas_projetos_zerados_cemei_alimentacao,
    ):
        lista_erros = validate_medicao_cemei_programas_e_projetos(
            solicitacao_medicao_finaliza_programas_projetos_zerados_cemei_alimentacao,
            [],
        )

        assert any(MSG_ERRO_PERIODOS_ZERADOS in erro["erro"] for erro in lista_erros)


class TestValidateMedicaoCemeiEmei:

    def test_ignora_integral_programas_e_solicitacoes_alimentacao(
        self, escola_cemei, categoria_medicao
    ):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_periodo(solicitacao, "INTEGRAL")
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.PROGRAMAS_E_PROJETOS)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.SOLICITACOES_DE_ALIMENTACAO)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.INFANTIL_MANHA)

        with patch(
            "src.medicao_inicial.validators._validate_medicao_emei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_emei(solicitacao, [])

        assert mock_validate.call_count == 1

    def test_nao_processa_quando_so_ha_grupos_ignorados(
        self, escola_cemei, categoria_medicao
    ):
        solicitacao = _cria_solicitacao(escola_cemei)
        _cria_medicao_com_grupo(solicitacao, GrupoMedicao.PROGRAMAS_E_PROJETOS)

        with patch(
            "src.medicao_inicial.validators._validate_medicao_emei_cemei",
            return_value=[],
        ) as mock_validate:
            validate_medicao_cemei_emei(solicitacao, [])

        assert mock_validate.call_count == 0
