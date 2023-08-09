import datetime
from unittest.mock import Mock, patch

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from sme_terceirizadas.medicao_inicial.models import SolicitacaoMedicaoInicial
from sme_terceirizadas.medicao_inicial.tasks import (
    cria_solicitacao_medicao_inicial_mes_atual,
    gera_pdf_relatorio_solicitacao_medicao_por_escola_async
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
