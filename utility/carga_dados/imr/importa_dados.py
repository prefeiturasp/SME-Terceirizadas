from openpyxl import load_workbook

from sme_terceirizadas.imr.models import ImportacaoPlanilhaTipoPenalidade
from sme_terceirizadas.perfil.models import Usuario
from utility.carga_dados.perfil.schemas import (
    ImportacaoPlanilhaUsuarioPerfilEscolaSchema,
)


class ProcessaPlanilhaTipoPenalidade:
    def __init__(
        self,
        usuario: Usuario,
        arquivo: ImportacaoPlanilhaTipoPenalidade,
        class_schema: ImportacaoPlanilhaUsuarioPerfilEscolaSchema,
    ) -> None:
        """Prepara atributos importantes para o processamento da planilha."""
        self.usuario = usuario
        self.arquivo = arquivo
        self.class_schema = class_schema
        self.erros = []
        self.worksheet = self.abre_worksheet()

    @property
    def path(self):
        return self.arquivo.conteudo.path

    def abre_worksheet(self):
        return load_workbook(self.path).active
