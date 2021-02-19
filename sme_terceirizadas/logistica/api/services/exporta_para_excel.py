from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


class RequisicoesExcelService(object):

    @classmethod
    def exportar(cls, requisioes):

        cabecalho = []
