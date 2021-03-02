from io import BytesIO

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


class RequisicoesExcelService(object):

    @classmethod
    def exportar(cls, requisioes):

        cabecalho = ['Número da Requisição', 'Status da Requisição', 'Quantidade Total de Guias', 'Número da Guia',
                     'Data de Entrega', 'Código CODAE da UE', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE',
                     'CEP UE', 'Cidade UE', 'Estado UE', 'Contato de Entrega', 'Telefone UE', 'Nome do Alimento',
                     'Código SUPRI', 'Código PAPA', 'Descrição Embalagem Fechada', 'Capacidade da Embalagem Fechada',
                     'Unidade de Medida da Embalagem Fechada', 'Quantidade de Volumes da Embalagem Fechada',
                     'Descrição Embalagem Fracionada', 'Capacidade da Embalagem Fracionada',
                     'Unidade de Medida da Embalagem Fracionada', 'Quantidade de Volumes da Embalagem Fracionada']

        wb = Workbook()
        ws = wb.active
        ws.title = 'Visão Analítica Abastecimento'

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = title
            length = len(title) + 2
            ws.column_dimensions[celula.column_letter].width = length

        for ind, requisicao in enumerate(requisioes, 2):
            ws.cell(row=ind, column=1, value=requisicao['numero_solicitacao'])
            ws.cell(row=ind, column=2, value=requisicao['status_requisicao'])
            ws.cell(row=ind, column=3, value=requisicao['quantidade_total_guias'])
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
            ws.cell(row=ind, column=16, value=requisicao['guias__alimentos__nome_alimento'])
            ws.cell(row=ind, column=17, value=requisicao['guias__alimentos__codigo_suprimento'])
            ws.cell(row=ind, column=18, value=requisicao['guias__alimentos__codigo_papa'])
            if requisicao['guias__alimentos__embalagens__tipo_embalagem'] == 'FECHADA':
                ws.cell(row=ind, column=19, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=20, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=21, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=22, value=requisicao['guias__alimentos__embalagens__qtd_volume'])
            else:
                ws.cell(row=ind, column=23, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=24, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=25, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=26, value=requisicao['guias__alimentos__embalagens__qtd_volume'])

        arquivo = BytesIO(save_virtual_workbook(wb))
        filename = 'visao-consolidada.xlsx'

        return {'arquivo': arquivo, 'filename': filename}
