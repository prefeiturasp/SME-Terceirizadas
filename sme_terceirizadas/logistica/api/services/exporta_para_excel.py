from io import BytesIO

from django.db.models.aggregates import Count
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from config.settings.base import MEDIA_ROOT
from sme_terceirizadas.logistica.models import SolicitacaoRemessa


class RequisicoesExcelService(object):

    @classmethod
    def exportar(cls, requisioes):
        r = SolicitacaoRemessa.objects.all().annotate(qtd_guias=Count('guias')).values(
            'numero_solicitacao', 'status', 'qtd_guias', 'guias__numero_guia', 'guias__data_entrega',
            'guias__codigo_unidade', 'guias__nome_unidade', 'guias__endereco_unidade', 'guias__endereco_unidade',
            'guias__numero_unidade', 'guias__bairro_unidade', 'guias__cep_unidade', 'guias__cidade_unidade',
            'guias__estado_unidade', 'guias__contato_unidade', 'guias__telefone_unidade')
        # cabecalho = ['Número da Requisição', 'Status da Requisição', 'Quantidade Total de Guias', 'Número da Guia',
        #              'Data de Entrega', 'Código CODAE da UE', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE',
        #              'CEP UE', 'Cidade UE', 'Estado UE', 'Contato de Entrega', 'Telefone UE', 'Nome do Alimento',
        #              'Código SUPRI', 'Código PAPA', 'Descrição Embalagem Fechada', 'Capacidade da Embalagem Fechada',
        #              'Unidade de Medida da Embalagem Fechada', 'Quantidade de Volumes da Embalagem Fechada',
        #              'Descrição Embalagem Fracionada', 'Capacidade da Embalagem Fracionada',
        #              'Unidade de Medida da Embalagem Fracionada', 'Quantidade de Volumes da Embalagem Fracionada']
        cabecalho = ['Número da Requisição', 'Status da Requisição', 'Quantidade Total de Guias', 'Número da Guia',
                     'Data de Entrega', 'Código CODAE da UE', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE',
                     'CEP UE', 'Cidade UE', 'Estado UE', 'Contato de Entrega', 'Telefone UE']

        wb = Workbook()
        ws = wb.active
        ws.title = "Visão Analítica Abastecimento"

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = title
            length = len(title) + 2
            ws.column_dimensions[celula.column_letter].width = length

        for ind, requisicao in enumerate(requisioes, 2):
            ws.cell(row=ind, column=1, value=requisicao['numero_solicitacao'])
            ws.cell(row=ind, column=2, value=requisicao['status'])
            ws.cell(row=ind, column=3, value=requisicao['qtd_guias'])
            ws.cell(row=ind, column=4, value=requisicao['guias__numero_guia'])
            ws.cell(row=ind, column=5, value=requisicao['guias__data_entrega'])
            ws.cell(row=ind, column=6, value=requisicao['guias__codigo_unidade'])
            ws.cell(row=ind, column=7, value=requisicao['guias__nome_unidade'])
            ws.cell(row=ind, column=8, value=requisicao['guias__endereco_unidade'])
            ws.cell(row=ind, column=9, value=requisicao['guias__numero_unidade'])
            ws.cell(row=ind, column=10, value=requisicao['guias__bairro_unidade'])
            ws.cell(row=ind, column=11, value=requisicao['guias__cep_unidade'])
            ws.cell(row=ind, column=12, value=requisicao['guias__cidade_unidade'])
            ws.cell(row=ind, column=13, value=requisicao['guias__estado_unidade'])
            ws.cell(row=ind, column=14, value=requisicao['guias__contato_unidade'])
            ws.cell(row=ind, column=15, value=requisicao['guias__telefone_unidade'])

        # result = BytesIO(save_virtual_workbook(wb))
        # filename = 'visao-consolidada.xlsx'
        wb.save('/Users/kelwy/Desktop/visao-analitica-abastecimento.xlsx')

        return 'feito'
