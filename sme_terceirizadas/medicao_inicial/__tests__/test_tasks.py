import datetime
from unittest.mock import Mock, patch

import pytest
from dateutil.relativedelta import relativedelta
from django.test import TestCase

from sme_terceirizadas.escola.models import AlunoPeriodoParcial
from sme_terceirizadas.medicao_inicial.models import Responsavel, SolicitacaoMedicaoInicial
from sme_terceirizadas.medicao_inicial.tasks import (
    buscar_solicitacao_mes_anterior,
    copiar_alunos_periodo_parcial,
    copiar_responsaveis,
    cria_solicitacao_medicao_inicial_mes_atual,
    criar_nova_solicitacao,
    gera_pdf_relatorio_solicitacao_medicao_por_escola_async,
    solicitacao_medicao_atual_existe
)


class CriaSolicitacaoMedicaoInicialMesAtualTest(TestCase):

    @patch('sme_terceirizadas.medicao_inicial.tasks.Escola.objects.all')
    @patch('sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.filter')
    @patch('sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.get')
    @patch('sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.create')
    @patch('sme_terceirizadas.medicao_inicial.tasks.logger.info')
    def test_cria_solicitacao_medicao_inicial_mes_atual(
        self, mock_logger_info, mock_create, mock_get, mock_filter, mock_all
    ):
        data_hoje = datetime.date.today()
        data_mes_anterior = data_hoje + relativedelta(months=-1)
        escola_nome_mock = 'escola1'
        mock_all.return_value = [Mock(nome=escola_nome_mock)]
        mock_filter.return_value.exists.return_value = False
        mock_get.side_effect = SolicitacaoMedicaoInicial.DoesNotExist

        cria_solicitacao_medicao_inicial_mes_atual()

        message = (f'x-x-x-x Não existe Solicitação de Medição Inicial para a escola {escola_nome_mock} no '
                   f'mês anterior ({data_mes_anterior.month:02d}/{data_mes_anterior.year}) x-x-x-x')
        mock_logger_info.assert_called_with(message)


class GeraPDFRelatorioSolicitacaoMedicaoPorEscolaAsyncTest(TestCase):

    @patch('sme_terceirizadas.medicao_inicial.tasks.gera_objeto_na_central_download')
    @patch('sme_terceirizadas.medicao_inicial.tasks.atualiza_central_download')
    @patch('sme_terceirizadas.relatorios.relatorios.relatorio_solicitacao_medicao_por_escola')
    @patch('sme_terceirizadas.medicao_inicial.tasks.SolicitacaoMedicaoInicial.objects.get')
    @patch('sme_terceirizadas.medicao_inicial.tasks.logger.info')
    def test_gera_pdf_relatorio_solicitacao_medicao_por_escola_async(
        self, mock_logger_info, mock_get, mock_relatorio, mock_atualiza, mock_gera_objeto
    ):
        mock_gera_objeto.return_value = Mock()
        mock_relatorio.return_value = 'arquivo_mock'
        uuid_mock = '123456-abcd-7890'

        gera_pdf_relatorio_solicitacao_medicao_por_escola_async('user', 'nome_arquivo', uuid_mock)

        mock_relatorio.assert_called_with(mock_get.return_value)
        mock_atualiza.assert_called_with(mock_gera_objeto.return_value, 'nome_arquivo', 'arquivo_mock')


@pytest.fixture
def solicitacao_mes_atual(escola_cei):
    data = datetime.date.today()
    return SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=data.year, mes=f'{data.month:02d}')


@pytest.mark.django_db
def test_solicitacao_medicao_atual_existe(escola_cei, solicitacao_mes_atual):
    data = datetime.date.today()

    assert solicitacao_medicao_atual_existe(escola_cei, data) is True
    assert solicitacao_medicao_atual_existe(escola_cei, data + relativedelta(months=-1)) is False


@pytest.mark.django_db
def test_buscar_solicitacao_mes_anterior(escola_cei):
    data = datetime.date.today() + relativedelta(months=-1)
    SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=data.year, mes=f'{data.month:02d}')

    assert buscar_solicitacao_mes_anterior(escola_cei, data) is not None


@pytest.mark.django_db
def test_criar_nova_solicitacao(escola_cei, solicitacao_mes_atual):
    data_hoje = datetime.date.today()

    solicitacao = criar_nova_solicitacao(solicitacao_mes_atual, escola_cei, data_hoje + relativedelta(months=1))
    assert solicitacao.escola == escola_cei


@pytest.mark.django_db
def test_copiar_responsaveis(escola_cei):
    solicitacao_origem = SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=2020, mes='01')
    Responsavel.objects.create(solicitacao_medicao_inicial=solicitacao_origem, nome='Responsavel Teste', rf='12345')

    solicitacao_destino = SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=2020, mes='02')
    copiar_responsaveis(solicitacao_origem, solicitacao_destino)

    assert solicitacao_destino.responsaveis.count() == 1
    assert solicitacao_destino.responsaveis.first().nome == 'Responsavel Teste'


@pytest.mark.django_db
def test_copiar_alunos_periodo_parcial(escola_cei, aluno):

    solicitacao_origem = SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=2020, mes='01')

    AlunoPeriodoParcial.objects.create(solicitacao_medicao_inicial=solicitacao_origem, aluno=aluno, escola=escola_cei)

    solicitacao_destino = SolicitacaoMedicaoInicial.objects.create(escola=escola_cei, ano=2020, mes='02')
    copiar_alunos_periodo_parcial(solicitacao_origem, solicitacao_destino)

    assert solicitacao_destino.alunos_periodo_parcial.count() == 1
    assert solicitacao_destino.alunos_periodo_parcial.first().aluno == aluno
