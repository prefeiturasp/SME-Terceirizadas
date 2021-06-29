import os
from io import BytesIO
from tempfile import NamedTemporaryFile

from openpyxl import Workbook
from openpyxl.styles import Border, Font, PatternFill, Side
from openpyxl.writer.excel import save_virtual_workbook

from ..helpers import (
    retorna_ocorrencias_alimento,
    retorna_status_alimento,
    retorna_status_guia_remessa,
    valida_rf_ou_cpf
)


class RequisicoesExcelService(object):
    DEFAULT_BORDER = Border(right=Side(border_style='thin', color='24292E'),
                            left=Side(border_style='thin', color='24292E'),
                            top=Side(border_style='thin', color='24292E'),
                            bottom=Side(border_style='thin', color='24292E'))

    @classmethod  # noqa C901
    def aplicar_estilo_padrao(cls, ws, count_data, count_fields):

        for linha in range(1, (count_data + 2)):
            for coluna in range(1, (count_fields + 1)):
                celula = ws.cell(row=linha, column=coluna)
                celula.border = cls.DEFAULT_BORDER
                if linha == 1:
                    celula.fill = PatternFill(fill_type='solid', fgColor='198459')

        # Ajuste automatico do tamanho das colunas
        for colunas in ws.columns:
            unmerged_cells = list(
                filter(lambda cell_to_check: cell_to_check.coordinate not in ws.merged_cells, colunas))
            length = max(len(str(cell.value)) for cell in unmerged_cells)
            ws.column_dimensions[unmerged_cells[0].column_letter].width = length * 1.2

    @classmethod
    def exportar_visao_distribuidor(cls, requisicoes):

        cabecalho = ['Número da Requisição', 'Status da Requisição', 'Quantidade Total de Guias', 'Número da Guia',
                     'Data de Entrega', 'Código CODAE da UE', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE',
                     'CEP UE', 'Cidade UE', 'Estado UE', 'Contato de Entrega', 'Telefone UE', 'Nome do Alimento',
                     'Código SUPRI', 'Código PAPA', 'Descrição Embalagem Fechada', 'Capacidade da Embalagem Fechada',
                     'Unidade de Medida da Embalagem Fechada', 'Quantidade de Volumes da Embalagem Fechada',
                     'Descrição Embalagem Fracionada', 'Capacidade da Embalagem Fracionada',
                     'Unidade de Medida da Embalagem Fracionada', 'Quantidade de Volumes da Embalagem Fracionada']

        count_fields = len(cabecalho)
        count_data = requisicoes.count()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Visão Analítica Abastecimento'

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = title
            celula.font = Font(size='13', bold=True, color='00FFFFFF')

        for ind, requisicao in enumerate(requisicoes, 2):
            ws.cell(row=ind, column=1, value=requisicao['numero_solicitacao'])
            ws.cell(row=ind, column=2, value=requisicao['status_requisicao'])
            ws.cell(row=ind, column=3, value=requisicao['quantidade_total_guias'])
            ws.cell(row=ind, column=4, value=requisicao['guias__numero_guia'])
            ws.cell(row=ind, column=5, value=requisicao['guias__data_entrega'])
            ws.cell(row=ind, column=6, value=requisicao['guias__codigo_unidade'])
            ws.cell(row=ind, column=7, value=requisicao['guias__nome_unidade'])
            ws.cell(row=ind, column=8, value=requisicao['guias__endereco_unidade'])
            ws.cell(row=ind, column=9, value=int(requisicao['guias__numero_unidade']))
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

        cls.aplicar_estilo_padrao(ws, count_data, count_fields)
        arquivo = BytesIO(save_virtual_workbook(wb))
        filename = 'visao-consolidada.xlsx'

        return {'arquivo': arquivo, 'filename': filename}

    @classmethod
    def exportar_visao_dilog(cls, requisicoes):

        cabecalho = ['Nome do Distribuidor', 'Número da Requisição', 'Status da Requisição',
                     'Quantidade Total de Guias', 'Número da Guia', 'Data de Entrega', 'Código EOL da UE',
                     'Código CODAE da UE', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE', 'CEP UE', 'Cidade UE',
                     'Estado UE', 'Contato de Entrega', 'Telefone UE', 'Nome do Alimento', 'Código SUPRI',
                     'Código PAPA', 'Descrição Embalagem Fechada', 'Capacidade da Embalagem Fechada',
                     'Unidade de Medida da Embalagem Fechada', 'Quantidade de Volumes da Embalagem Fechada',
                     'Descrição Embalagem Fracionada', 'Capacidade da Embalagem Fracionada',
                     'Unidade de Medida da Embalagem Fracionada', 'Quantidade de Volumes da Embalagem Fracionada',
                     'Status da Guia']

        count_fields = len(cabecalho)
        count_data = requisicoes.count()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Visão Analítica Abastecimento'

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = title
            celula.font = Font(size='13', bold=True, color='00FFFFFF')

        for ind, requisicao in enumerate(requisicoes, 2):
            ws.cell(row=ind, column=1, value=requisicao['distribuidor__nome_fantasia'])
            ws.cell(row=ind, column=2, value=requisicao['numero_solicitacao'])
            ws.cell(row=ind, column=3, value=requisicao['status_requisicao'])
            ws.cell(row=ind, column=4, value=requisicao['quantidade_total_guias'])
            ws.cell(row=ind, column=5, value=requisicao['guias__numero_guia'])
            ws.cell(row=ind, column=6, value=requisicao['guias__data_entrega'])
            ws.cell(row=ind, column=7, value=requisicao['codigo_eol_unidade'])
            ws.cell(row=ind, column=8, value=requisicao['guias__codigo_unidade'])
            ws.cell(row=ind, column=9, value=requisicao['guias__nome_unidade'])
            ws.cell(row=ind, column=10, value=requisicao['guias__endereco_unidade'])
            ws.cell(row=ind, column=11, value=int(requisicao['guias__numero_unidade']))
            ws.cell(row=ind, column=12, value=requisicao['guias__bairro_unidade'])
            ws.cell(row=ind, column=13, value=requisicao['guias__cep_unidade'])
            ws.cell(row=ind, column=14, value=requisicao['guias__cidade_unidade'])
            ws.cell(row=ind, column=15, value=requisicao['guias__estado_unidade'])
            ws.cell(row=ind, column=16, value=requisicao['guias__contato_unidade'])
            ws.cell(row=ind, column=17, value=requisicao['guias__telefone_unidade'])
            ws.cell(row=ind, column=18, value=requisicao['guias__alimentos__nome_alimento'])
            ws.cell(row=ind, column=19, value=requisicao['guias__alimentos__codigo_suprimento'])
            ws.cell(row=ind, column=20, value=requisicao['guias__alimentos__codigo_papa'])
            if requisicao['guias__alimentos__embalagens__tipo_embalagem'] == 'FECHADA':
                ws.cell(row=ind, column=21, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=22, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=23, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=24, value=requisicao['guias__alimentos__embalagens__qtd_volume'])
            else:
                ws.cell(row=ind, column=25, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=26, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=27, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=28, value=requisicao['guias__alimentos__embalagens__qtd_volume'])
            ws.cell(row=ind, column=29, value=requisicao['guias__status'])

        cls.aplicar_estilo_padrao(ws, count_data, count_fields)
        arquivo = BytesIO(save_virtual_workbook(wb))
        filename = 'visao-consolidada.xlsx'

        return {'arquivo': arquivo, 'filename': filename}

    @classmethod # noqa C901
    def exportar_entregas_distribuidor(cls, requisicoes):

        cabecalho = ['Número da Requisição', 'Quantidade Total de Guias', 'Número da Guia', 'Data de Entrega',
                     '(1ª Conferência) Data de recebimento', '(1ª Conferência) Hora de recebimento',
                     '(1ª Conferência) Nome do Motorista', '(1ª Conferência) Placa do Veículo',
                     'Data de Registro da 1ª Conferência', 'Hora de Registro da 1ª Conferência',
                     '(Reposição) Data de recebimento', '(Reposição) Hora de recebimento',
                     '(Reposição) Nome do Motorista', '(Reposição) Placa do Veículo',
                     'Data de Registro da Reposição', 'Hora de Registro da Reposição',
                     'Código CODAE', 'Código EOL', 'Nome UE', 'Endereço UE', 'Número UE', 'Bairro UE',
                     'CEP UE', 'Cidade UE', 'Estado UE', 'Contato de Entrega', 'Telefone UE', 'Nome do Alimento',
                     'Código SUPRI', 'Código PAPA',
                     'Descrição Embalagem Fechada', 'Capacidade da Embalagem Fechada',
                     'Unidade de Medida da Embalagem Fechada',
                     'Quantidade Prevista (Volumes da Embalagem Fechada)',
                     'Quantidade Recebida (Volumes da Embalagem Fechada)',
                     'Quantidade a Receber (Volumes da Embalagem Fechada)',
                     'Quantidade Reposta (Volumes da Embalagem Fechada)',
                     'Descrição Embalagem Fracionada', 'Capacidade da Embalagem Fracionada',
                     'Unidade de Medida da Embalagem Fracionada',
                     'Quantidade Prevista (Volumes da Embalagem Fracionada)',
                     'Quantidade Recebida (Volumes da Embalagem Fracionada)',
                     'Quantidade a Receber (Volumes da Embalagem Fracionada)',
                     'Quantidade Reposta (Volumes da Embalagem Fracionada)',
                     '(1ª Conferência) Status de Recebimento do Alimento', '(1ª Conferência) Ocorrência',
                     '(1ª Conferência) Observações',
                     '(1ª Conferência) Nome Completo do Conferente',
                     '(1ª Conferência) Documento do Conferente (RF ou CPF)',
                     '(Reposição) Status de Recebimento do Alimento', '(Reposição) Ocorrência',
                     '(Reposição) Observações',
                     '(Reposição) Nome Completo do Conferente', '(Reposição) Documento do Conferente (RF ou CPF)',
                     'Status da Guia de Remessa'

                     ]

        count_fields = len(cabecalho)
        count_data = requisicoes.count()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Visão Analítica Abastecimento'

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = title
            celula.font = Font(size='13', bold=True, color='00FFFFFF')

        for ind, requisicao in enumerate(requisicoes, 2):

            qtd_recebida = 0

            if 'conferencia_alimento' in requisicao and requisicao['conferencia_alimento'] is not None:
                qtd_recebida = requisicao['conferencia_alimento'].qtd_recebido
            elif 'primeira_conferencia' in requisicao:
                qtd_recebida = requisicao['guias__alimentos__embalagens__qtd_volume']
            else:
                qtd_recebida = ''

            ws.cell(row=ind, column=1, value=requisicao['numero_solicitacao'])
            ws.cell(row=ind, column=2, value=requisicao['quantidade_total_guias'])
            ws.cell(row=ind, column=3, value=requisicao['guias__numero_guia'])
            ws.cell(row=ind, column=4, value=requisicao['guias__data_entrega'])
            if 'primeira_conferencia' in requisicao:
                ws.cell(row=ind, column=5, value=requisicao['primeira_conferencia'].data_recebimento)
                ws.cell(row=ind, column=6, value=requisicao['primeira_conferencia'].hora_recebimento)
                ws.cell(row=ind, column=7, value=requisicao['primeira_conferencia'].nome_motorista)
                ws.cell(row=ind, column=8, value=requisicao['primeira_conferencia'].placa_veiculo)
                ws.cell(row=ind, column=9, value=requisicao['primeira_conferencia'].criado_em.strftime('%d/%m/%Y'))
                ws.cell(row=ind, column=10, value=requisicao['primeira_conferencia'].criado_em.strftime('%H:%M:%S'))

            if 'primeira_reposicao' in requisicao:
                ws.cell(row=ind, column=11, value=requisicao['primeira_reposicao'].data_recebimento)
                ws.cell(row=ind, column=12, value=requisicao['primeira_reposicao'].hora_recebimento)
                ws.cell(row=ind, column=13, value=requisicao['primeira_reposicao'].nome_motorista)
                ws.cell(row=ind, column=14, value=requisicao['primeira_reposicao'].placa_veiculo)
                ws.cell(row=ind, column=15, value=requisicao['primeira_reposicao'].criado_em.strftime('%d/%m/%Y'))
                ws.cell(row=ind, column=16, value=requisicao['primeira_reposicao'].criado_em.strftime('%H:%M:%S'))
            ws.cell(row=ind, column=17, value=requisicao['guias__codigo_unidade'])
            ws.cell(row=ind, column=18, value=requisicao['guias__escola__codigo_eol'])
            ws.cell(row=ind, column=19, value=requisicao['guias__nome_unidade'])
            ws.cell(row=ind, column=20, value=requisicao['guias__endereco_unidade'])
            ws.cell(row=ind, column=21, value=int(requisicao['guias__numero_unidade']))
            ws.cell(row=ind, column=22, value=requisicao['guias__bairro_unidade'])
            ws.cell(row=ind, column=23, value=requisicao['guias__cep_unidade'])
            ws.cell(row=ind, column=24, value=requisicao['guias__cidade_unidade'])
            ws.cell(row=ind, column=25, value=requisicao['guias__estado_unidade'])
            ws.cell(row=ind, column=26, value=requisicao['guias__contato_unidade'])
            ws.cell(row=ind, column=27, value=requisicao['guias__telefone_unidade'])
            ws.cell(row=ind, column=28, value=requisicao['guias__alimentos__nome_alimento'])
            ws.cell(row=ind, column=29, value=requisicao['guias__alimentos__codigo_suprimento'])
            ws.cell(row=ind, column=30, value=requisicao['guias__alimentos__codigo_papa'])

            if requisicao['guias__alimentos__embalagens__tipo_embalagem'] == 'FECHADA':
                ws.cell(row=ind, column=31, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=32, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=33, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=34, value=requisicao['guias__alimentos__embalagens__qtd_volume'])
                ws.cell(row=ind, column=35, value=qtd_recebida)
                ws.cell(row=ind, column=36, value=requisicao['guias__alimentos__embalagens__qtd_a_receber'])
                if 'reposicao_alimento' in requisicao:
                    ws.cell(row=ind, column=37, value=requisicao['reposicao_alimento'].qtd_recebido)
            else:
                ws.cell(row=ind, column=38, value=requisicao['guias__alimentos__embalagens__descricao_embalagem'])
                ws.cell(row=ind, column=39, value=requisicao['guias__alimentos__embalagens__capacidade_embalagem'])
                ws.cell(row=ind, column=40, value=requisicao['guias__alimentos__embalagens__unidade_medida'])
                ws.cell(row=ind, column=41, value=requisicao['guias__alimentos__embalagens__qtd_volume'])
                ws.cell(row=ind, column=42, value=qtd_recebida)
                ws.cell(row=ind, column=43, value=requisicao['guias__alimentos__embalagens__qtd_a_receber'])
                if 'reposicao_alimento' in requisicao:
                    ws.cell(row=ind, column=44, value=requisicao['reposicao_alimento'].qtd_recebido)

            if 'primeira_conferencia' in requisicao:
                if 'conferencia_alimento' in requisicao:
                    ws.cell(row=ind, column=45, value=retorna_status_alimento(
                        requisicao['conferencia_alimento'].status_alimento
                    ))
                    ws.cell(row=ind, column=46, value=retorna_ocorrencias_alimento(
                        requisicao['conferencia_alimento'].ocorrencia
                    ))
                    ws.cell(row=ind, column=47, value=requisicao['conferencia_alimento'].observacao)
                ws.cell(row=ind, column=48, value=requisicao['primeira_conferencia'].criado_por.nome)
                ws.cell(row=ind, column=49, value=valida_rf_ou_cpf(requisicao['primeira_conferencia'].criado_por))

            if 'primeira_reposicao' in requisicao:
                if 'reposicao_alimento' in requisicao:
                    ws.cell(row=ind, column=50, value=retorna_status_alimento(
                        requisicao['reposicao_alimento'].status_alimento
                    ))
                    ws.cell(row=ind, column=51, value=retorna_ocorrencias_alimento(
                        requisicao['reposicao_alimento'].ocorrencia
                    ))
                    ws.cell(row=ind, column=52, value=requisicao['reposicao_alimento'].observacao)
                    ws.cell(row=ind, column=53, value=requisicao['primeira_reposicao'].criado_por.nome)
                    ws.cell(row=ind, column=54, value=valida_rf_ou_cpf(requisicao['primeira_reposicao'].criado_por))

            ws.cell(row=ind, column=55, value=retorna_status_guia_remessa(requisicao['guias__status']))

        cls.aplicar_estilo_padrao(ws, count_data, count_fields)
        with NamedTemporaryFile(delete=False) as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            arquivo = tmp.read()
            tmp.close()
            os.unlink(tmp.name)
        filename = 'visao-consolidada.xlsx'

        return {'arquivo': arquivo, 'filename': filename}
