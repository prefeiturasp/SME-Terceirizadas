import logging

from openpyxl import load_workbook

from sme_terceirizadas.dieta_especial.models import ArquivoCargaDietaEspecial

logger = logging.getLogger('sigpae.importa_dietas_especiais')



class ProcessadorPlanilha:
    def __init__(self, arquivo: ArquivoCargaDietaEspecial) -> None:
        self.arquivo = arquivo
    
    @property
    def path(self):
        return self.arquivo.conteudo.path
    
    def iniciar_processamento(self):
        self.arquivo.inicia_processamento()
        if not self.validacao_inicial():
            return

        workbook = load_workbook(self.path)
        worksheet = workbook.active
        linhas = list(worksheet.rows)
        logger.debug(f'len: {len(linhas)} : qt colunas {len(linhas[0])} : worksheet: {worksheet.max_column}')

        for linha in linhas:
            print(linha[0].value, linha[1].value, linha[2].value, linha[3].value, linha[4].value, linha[5].value, linha[6].value,linha[7].value,linha[8].value, linha[9].value, linha[10].value, linha[11].value)
            break

    def validacao_inicial(self):
        return (self.existe_conteudo() and self.extensao_do_arquivo_esta_correta())

    def existe_conteudo(self):
        if not self.arquivo.conteudo:
            self.arquivo.log = 'Não foi feito o upload da planilha'
            self.arquivo.erro_no_processamento()
            return False
        return True

    def extensao_do_arquivo_esta_correta(self):
        if not self.path.endswith('.xlsx'):
            self.arquivo.log = 'Planilha precisa ter extensão .xlsx'
            self.arquivo.erro_no_processamento()
            return False
        return True


def importa_dietas_especiais(arquivo: ArquivoCargaDietaEspecial):
    logger.debug(f'Iniciando o processamento do arquivo: {arquivo.uuid}')
    
    processador = ProcessadorPlanilha(arquivo)

    try:
        processador.iniciar_processamento()
    except Exception as e:
        pass


