import logging

from sme_terceirizadas.dados_comuns.behaviors import StatusAtivoInativo
from sme_terceirizadas.imr.models import (
    ImportacaoPlanilhaTipoOcorrencia,
    ImportacaoPlanilhaTipoPenalidade,
    ObrigacaoPenalidade,
    TipoGravidade,
    TipoPenalidade,
)
from sme_terceirizadas.perfil.models import Usuario
from sme_terceirizadas.terceirizada.models import Edital
from utility.carga_dados.imr.schemas import (
    ImportacaoPlanilhaTipoOcorrenciaSchema,
    ImportacaoPlanilhaTipoPenalidadeSchema,
)
from utility.carga_dados.processador_planilha_generico.models import (
    ProcessadorDePlanilha,
)


def importa_tipos_penalidade(
    usuario: Usuario, arquivo: ImportacaoPlanilhaTipoPenalidade
) -> None:
    logger = logging.getLogger("sigpae.carga_dados_tipo_penalidade_importa_dados")
    logger.debug(f"Iniciando o processamento do arquivo: {arquivo.uuid}")

    try:
        processador = ProcessadorPlanilhaTipoPenalidade(
            usuario,
            arquivo,
            ImportacaoPlanilhaTipoPenalidadeSchema,
            "edital",
            "numero_clausula",
            logger,
        )
        processador.processamento()
        processador.finaliza_processamento()
    except Exception as exc:
        logger.error(f"Erro genérico: {exc}")


class ProcessadorPlanilhaTipoPenalidade(ProcessadorDePlanilha):
    def get_edital(self, numero_edital: str):
        return Edital.objects.get(numero=numero_edital)

    def get_tipo_gravidade(self, tipo_gravidade: str):
        return TipoGravidade.objects.get(tipo=tipo_gravidade)

    def cria_tipo_penalidade_obj(
        self,
        usuario_schema: ImportacaoPlanilhaTipoPenalidadeSchema,
    ):
        edital = self.get_edital(usuario_schema.edital)
        gravidade = self.get_tipo_gravidade(usuario_schema.gravidade)
        status = usuario_schema.status == StatusAtivoInativo.ATIVO
        tipo_penalidade, _ = TipoPenalidade.objects.update_or_create(
            edital=edital,
            numero_clausula=usuario_schema.numero_clausula,
            defaults={
                "criado_por": self.usuario,
                "gravidade": gravidade,
                "descricao": usuario_schema.descricao_clausula,
                "status": status,
            },
        )
        return tipo_penalidade

    def normaliza_obrigacoes(self, obrigacoes: str):
        if obrigacoes[-1] == ";":
            obrigacoes = obrigacoes[: len(obrigacoes) - 1]
        return obrigacoes.split(";")

    def cria_obrigacao_penalidade(
        self, tipo_penalidade: TipoPenalidade, descricao: str
    ):
        ObrigacaoPenalidade.objects.create(
            tipo_penalidade=tipo_penalidade, descricao=descricao
        )

    def cria_objeto(
        self, index: int, usuario_schema: ImportacaoPlanilhaTipoPenalidadeSchema
    ):
        tipo_penalidade = self.cria_tipo_penalidade_obj(usuario_schema)
        lista_obrigacoes = self.normaliza_obrigacoes(usuario_schema.obrigacoes)
        for descricao_obrigacao in lista_obrigacoes:
            self.cria_obrigacao_penalidade(tipo_penalidade, descricao_obrigacao)


def importa_tipos_ocorrencia(
    usuario: Usuario, arquivo: ImportacaoPlanilhaTipoOcorrencia
) -> None:
    logger = logging.getLogger("sigpae.carga_dados_tipo_ocorrencia_importa_dados")
    logger.debug(f"Iniciando o processamento do arquivo: {arquivo.uuid}")

    try:
        processador = ProcessadorPlanilhaTipoOcorrencia(
            usuario,
            arquivo,
            ImportacaoPlanilhaTipoOcorrenciaSchema,
            "edital",
            "numero_clausula",
            logger,
        )
        processador.processamento()
        processador.finaliza_processamento()
    except Exception as exc:
        logger.error(f"Erro genérico: {exc}")


class ProcessadorPlanilhaTipoOcorrencia(ProcessadorDePlanilha):
    def cria_objeto(
        self, index: int, usuario_schema: ImportacaoPlanilhaTipoOcorrenciaSchema
    ):
        pass
