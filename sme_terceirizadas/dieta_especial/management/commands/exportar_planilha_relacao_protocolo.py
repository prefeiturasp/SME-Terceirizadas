from django.core.management.base import BaseCommand
from openpyxl import Workbook
from openpyxl.styles import Font

from sme_terceirizadas.dieta_especial.models import SolicitacaoDietaEspecial
from sme_terceirizadas.terceirizada.models import Edital


class Command(BaseCommand):
    help = """
    Verifica se os protocolos padrões da planilha de importação estão cadastrados no sistema
    para determinado Edital e exporta uma planilha com o resultado
    """

    def formatar_tamanho_celulas(self, ws):
        for column in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            ws.column_dimensions[column].width = 25 if column in ['C', 'E', 'F', 'H'] else 50

    def exportar_planilha(self, cabecalho, dicts_para_planilha):
        wb = Workbook()
        ws = wb.active
        self.formatar_tamanho_celulas(ws)
        ws.title = 'Relação Protocolos'

        for ind, title in enumerate(cabecalho, 1):
            celula = ws.cell(row=1, column=ind)
            celula.value = str(title)
            celula.font = Font(size='13', bold=True)

        for ind, dict_solicitacao in enumerate(dicts_para_planilha, 2):
            ws.cell(row=ind, column=1, value=str(dict_solicitacao['UUID']))
            ws.cell(row=ind, column=2, value=dict_solicitacao['NOME ESCOLA'])
            ws.cell(row=ind, column=3, value=dict_solicitacao['COD EOL ESCOLA'])
            ws.cell(row=ind, column=4, value=dict_solicitacao['NOME ALUNO'])
            ws.cell(row=ind, column=5, value=dict_solicitacao['COD EOL ALUNO'])
            ws.cell(row=ind, column=6, value=dict_solicitacao['LOTE'])
            ws.cell(row=ind, column=7, value=dict_solicitacao['NOME PROTOCOLO IMPORTADO DIETA'])
            ws.cell(row=ind, column=8, value=dict_solicitacao['PROTOCOLO VALIDO'])

        wb.save('relacao-protocolos.xlsx')

    def handle(self, *args, **options):
        solicitacoes = SolicitacaoDietaEspecial.objects.filter(eh_importado=True)
        dicts_para_planilha = []
        for solicitacao in solicitacoes:
            nome_protocolo = solicitacao.nome_protocolo
            editais_uuids = solicitacao.escola.lote.contratos_do_lote.values_list('edital__uuid', flat=True)
            editais = Edital.objects.filter(uuid__in=editais_uuids)
            nomes_protocolos = editais.values_list('protocolos_padroes_dieta_especial__nome_protocolo', flat=True)
            dict_solicitacao = {
                'UUID': solicitacao.uuid,
                'NOME ESCOLA': solicitacao.escola.nome,
                'COD EOL ESCOLA': solicitacao.escola.codigo_eol,
                'NOME ALUNO': solicitacao.aluno.nome,
                'COD EOL ALUNO': solicitacao.aluno.codigo_eol,
                'LOTE': solicitacao.escola.lote.nome,
                'NOME PROTOCOLO IMPORTADO DIETA': nome_protocolo
            }
            dict_solicitacao['PROTOCOLO VALIDO'] = 'Sim' if nome_protocolo in nomes_protocolos else 'Não'
            dicts_para_planilha.append(dict_solicitacao)
        cabecalho = [key for key in dicts_para_planilha[0]]
        self.exportar_planilha(cabecalho, dicts_para_planilha)
