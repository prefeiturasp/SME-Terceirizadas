import datetime
from unittest.mock import Mock, patch

import pytest
from dateutil.relativedelta import relativedelta
from django.http import QueryDict
from django.test import TestCase

from sme_terceirizadas.dados_comuns.models import CentralDeDownload
from sme_terceirizadas.escola.models import AlunoPeriodoParcial
from sme_terceirizadas.medicao_inicial.models import (
    Responsavel,
    SolicitacaoMedicaoInicial,
)
from sme_terceirizadas.medicao_inicial.services.relatorio_adesao import obtem_resultados
from sme_terceirizadas.medicao_inicial.tasks import (
    buscar_solicitacao_mes_anterior,
    copiar_alunos_periodo_parcial,
    copiar_responsaveis,
    cria_solicitacao_medicao_inicial_mes_atual,
    criar_nova_solicitacao,
    exporta_relatorio_adesao_para_pdf,
    exporta_relatorio_adesao_para_xlsx,
    gera_pdf_relatorio_solicitacao_medicao_por_escola_async,
    gera_pdf_relatorio_unificado_async,
    solicitacao_medicao_atual_existe,
)


class CriaSolicitacaoMedicaoInicialMesAtualTest(TestCase):
    @patch("sme_terceirizadas.medicao_inicial.tasks.Escola.objects.all")
    @patch(
        "sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.filter"
    )
    @patch(
        "sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.get"
    )
    @patch(
        "sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.create"
    )
    @patch("sme_terceirizadas.medicao_inicial.tasks.logger.info")
    def test_cria_solicitacao_medicao_inicial_mes_atual(
        self, mock_logger_info, mock_create, mock_get, mock_filter, mock_all
    ):
        data_hoje = datetime.date.today()
        data_mes_anterior = data_hoje + relativedelta(months=-1)
        escola_nome_mock = "escola1"
        mock_all.return_value = [Mock(nome=escola_nome_mock)]
        mock_filter.return_value.exists.return_value = False
        mock_get.side_effect = SolicitacaoMedicaoInicial.DoesNotExist

        cria_solicitacao_medicao_inicial_mes_atual()

        message = (
            f"x-x-x-x Não existe Solicitação de Medição Inicial para a escola {escola_nome_mock} no "
            f"mês anterior ({data_mes_anterior.month:02d}/{data_mes_anterior.year}) x-x-x-x"
        )
        mock_logger_info.assert_called_with(message)


class GeraPDFRelatorioSolicitacaoMedicaoPorEscolaAsyncTest(TestCase):
    @patch("sme_terceirizadas.medicao_inicial.tasks.gera_objeto_na_central_download")
    @patch("sme_terceirizadas.medicao_inicial.tasks.atualiza_central_download")
    @patch(
        "sme_terceirizadas.relatorios.relatorios.relatorio_solicitacao_medicao_por_escola"
    )
    @patch(
        "sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.get"
    )
    @patch("sme_terceirizadas.medicao_inicial.tasks.logger.info")
    def test_gera_pdf_relatorio_solicitacao_medicao_por_escola_async(
        self,
        mock_logger_info,
        mock_get,
        mock_relatorio,
        mock_atualiza,
        mock_gera_objeto,
    ):
        mock_gera_objeto.return_value = Mock()
        mock_relatorio.return_value = "arquivo_mock"
        uuid_mock = "123456-abcd-7890"

        gera_pdf_relatorio_solicitacao_medicao_por_escola_async(
            "user", "nome_arquivo", uuid_mock
        )


class GeraPDFRelatorioUnificadoMedicoesIniciaisAsyncTest(TestCase):
    @patch("sme_terceirizadas.medicao_inicial.tasks.gera_objeto_na_central_download")
    @patch("sme_terceirizadas.medicao_inicial.tasks.atualiza_central_download")
    @patch(
        "sme_terceirizadas.relatorios.relatorios.relatorio_consolidado_medicoes_iniciais_emef"
    )
    @patch(
        "sme_terceirizadas.relatorios.relatorios.relatorio_solicitacao_medicao_por_escola"
    )
    @patch(
        "sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.get"
    )
    @patch("sme_terceirizadas.medicao_inicial.tasks.logger.info")
    def test_gera_pdf_relatorio_unificado_async(
        self,
        mock_logger_info,
        mock_get,
        mock_relatorio_somatorio,
        mock_relatorio_lançamentos,
        mock_atualiza,
        mock_gera_objeto,
    ):
        mock_gera_objeto.return_value = Mock()
        mock_relatorio_lançamentos.return_value = "arquivo_mock"
        uuid_mock = "123456-abcd-7890"
        tipos_de_unidade = ["EMEF", "CEUEMEF", "EMEFM", "EMEBS", "CIEJA", "CEU Gestão"]

        gera_pdf_relatorio_unificado_async(
            "user", "nome_arquivo", uuid_mock, tipos_de_unidade
        )


@pytest.fixture
def solicitacao_mes_atual(escola_cei):
    data = datetime.date.today()
    return SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=data.year, mes=f"{data.month:02d}"
    )


@pytest.mark.django_db
def test_solicitacao_medicao_atual_existe(escola_cei, solicitacao_mes_atual):
    data = datetime.date.today()

    assert solicitacao_medicao_atual_existe(escola_cei, data) is True
    assert (
        solicitacao_medicao_atual_existe(escola_cei, data + relativedelta(months=-1))
        is False
    )


@pytest.mark.django_db
def test_buscar_solicitacao_mes_anterior(escola_cei):
    data = datetime.date.today() + relativedelta(months=-1)
    SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=data.year, mes=f"{data.month:02d}"
    )

    assert buscar_solicitacao_mes_anterior(escola_cei, data) is not None


@pytest.mark.django_db
def test_criar_nova_solicitacao(escola_cei, solicitacao_mes_atual):
    data_hoje = datetime.date.today()

    solicitacao = criar_nova_solicitacao(
        solicitacao_mes_atual, escola_cei, data_hoje + relativedelta(months=1)
    )
    assert solicitacao.escola == escola_cei


@pytest.mark.django_db
def test_copiar_responsaveis(escola_cei):
    solicitacao_origem = SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=2020, mes="01"
    )
    Responsavel.objects.create(
        solicitacao_medicao_inicial=solicitacao_origem,
        nome="Responsavel Teste",
        rf="12345",
    )

    solicitacao_destino = SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=2020, mes="02"
    )
    copiar_responsaveis(solicitacao_origem, solicitacao_destino)

    assert solicitacao_destino.responsaveis.count() == 1
    assert solicitacao_destino.responsaveis.first().nome == "Responsavel Teste"


@pytest.mark.django_db
def test_copiar_alunos_periodo_parcial(escola_cei, aluno):
    solicitacao_origem = SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=2020, mes="01"
    )

    AlunoPeriodoParcial.objects.create(
        solicitacao_medicao_inicial=solicitacao_origem, aluno=aluno, escola=escola_cei
    )

    solicitacao_destino = SolicitacaoMedicaoInicial.objects.create(
        escola=escola_cei, ano=2020, mes="02"
    )
    copiar_alunos_periodo_parcial(solicitacao_origem, solicitacao_destino)

    assert solicitacao_destino.alunos_periodo_parcial.count() == 1
    assert solicitacao_destino.alunos_periodo_parcial.first().aluno == aluno


@pytest.mark.django_db
def test_exporta_relatorio_adesao_para_xlsx(
    usuario,
    categoria_medicao,
    tipo_alimentacao_refeicao,
    make_solicitacao_medicao_inicial,
    make_medicao,
    make_valores_medicao,
    make_periodo_escolar,
):
    # arrange
    mes = "03"
    ano = "2024"
    solicitacao = make_solicitacao_medicao_inicial(
        mes, ano, "MEDICAO_APROVADA_PELA_CODAE"
    )
    periodo_escolar = make_periodo_escolar("MANHA")
    medicao = make_medicao(solicitacao, periodo_escolar)

    valores = range(1, 6)

    for x in valores:
        make_valores_medicao(
            medicao=medicao,
            categoria_medicao=categoria_medicao,
            valor=str(x).rjust(2, "0"),
            tipo_alimentacao=tipo_alimentacao_refeicao,
        )
        make_valores_medicao(
            medicao=medicao,
            categoria_medicao=categoria_medicao,
            valor=str(x).rjust(2, "0"),
            nome_campo="frequencia",
        )

    nome_arquivo = "relatorio-adesao.xlsx"

    # act
    resultados = obtem_resultados(mes, ano, QueryDict())

    exporta_relatorio_adesao_para_xlsx(
        usuario, nome_arquivo, resultados, {"mes_ano": f"{mes}_{ano}"}
    )

    assert CentralDeDownload.objects.count() == 1
    arquivo = CentralDeDownload.objects.first()
    assert arquivo is not None and arquivo.usuario == usuario
    assert arquivo is not None and arquivo.identificador == nome_arquivo
    assert arquivo is not None and arquivo.status == CentralDeDownload.STATUS_CONCLUIDO


@pytest.mark.django_db
def test_exporta_relatorio_adesao_para_xlsx_sem_resultados(usuario):
    # arrange
    mes = "03"
    ano = "2024"

    nome_arquivo = "relatorio-adesao.xlsx"

    # act
    resultados = {}

    exporta_relatorio_adesao_para_xlsx(
        usuario, nome_arquivo, resultados, {"mes_ano": f"{mes}_{ano}"}
    )

    assert CentralDeDownload.objects.count() == 1
    arquivo = CentralDeDownload.objects.first()
    assert arquivo is not None and arquivo.usuario == usuario
    assert arquivo is not None and arquivo.identificador == nome_arquivo
    assert arquivo is not None and arquivo.status == CentralDeDownload.STATUS_CONCLUIDO


@pytest.mark.django_db
def test_exporta_relatorio_adesao_para_pdf(
    usuario,
    categoria_medicao,
    tipo_alimentacao_refeicao,
    make_solicitacao_medicao_inicial,
    make_medicao,
    make_valores_medicao,
    make_periodo_escolar,
):
    # arrange
    mes = "03"
    ano = "2024"
    solicitacao = make_solicitacao_medicao_inicial(
        mes, ano, "MEDICAO_APROVADA_PELA_CODAE"
    )
    periodo_escolar = make_periodo_escolar("MANHA")
    medicao = make_medicao(solicitacao, periodo_escolar)

    valores = range(1, 6)

    for x in valores:
        make_valores_medicao(
            medicao=medicao,
            categoria_medicao=categoria_medicao,
            valor=str(x).rjust(2, "0"),
            tipo_alimentacao=tipo_alimentacao_refeicao,
        )
        make_valores_medicao(
            medicao=medicao,
            categoria_medicao=categoria_medicao,
            valor=str(x).rjust(2, "0"),
            nome_campo="frequencia",
        )

    nome_arquivo = "relatorio-adesao.pdf"

    # act
    resultados = obtem_resultados(mes, ano, QueryDict())

    exporta_relatorio_adesao_para_pdf(
        usuario, nome_arquivo, resultados, {"mes_ano": f"{mes}_{ano}"}
    )

    assert CentralDeDownload.objects.count() == 1
    arquivo = CentralDeDownload.objects.first()
    assert arquivo is not None and arquivo.usuario == usuario
    assert arquivo is not None and arquivo.identificador == nome_arquivo
    assert arquivo is not None and arquivo.status == CentralDeDownload.STATUS_CONCLUIDO


@pytest.mark.django_db
def test_exporta_relatorio_adesao_para_pdf_sem_resultados(usuario):
    # arrange
    mes = "03"
    ano = "2024"

    nome_arquivo = "relatorio-adesao.pdf"

    # act
    resultados = {}

    exporta_relatorio_adesao_para_pdf(
        usuario, nome_arquivo, resultados, {"mes_ano": f"{mes}_{ano}"}
    )

    assert CentralDeDownload.objects.count() == 1
    arquivo = CentralDeDownload.objects.first()
    assert arquivo is not None and arquivo.usuario == usuario
    assert arquivo is not None and arquivo.identificador == nome_arquivo
    assert arquivo is not None and arquivo.status == CentralDeDownload.STATUS_CONCLUIDO
