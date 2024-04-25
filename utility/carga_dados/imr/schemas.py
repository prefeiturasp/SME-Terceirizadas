from typing import Optional

from pydantic import BaseModel, validator


class ImportacaoPlanilhaTipoPenalidadeSchema(BaseModel):
    edital: Optional[str]
    numero_clausula: Optional[str]
    gravidade: Optional[str]
    obrigacoes: Optional[str]
    descricao_clausula: Optional[str]
    status: Optional[str]

    @classmethod
    def checa_vazio(cls, value, nome_parametro):
        if not value:
            raise Exception(f"{nome_parametro} não pode ser vazio.")

    @validator("edital")
    def valida_edital(cls, value):
        cls.checa_vazio(value, "Edital")
        return value.strip()

    @validator("numero_clausula")
    def valida_numero_clausula(cls, value):
        cls.checa_vazio(value, "Número da Cláusula/Item")
        return value.strip()

    @validator("gravidade")
    def valida_gravidade(cls, value):
        cls.checa_vazio(value, "Gravidade")
        return value.strip()

    @validator("obrigacoes")
    def valida_obrigacoes(cls, value):
        cls.checa_vazio(value, "Obrigações")
        return value.strip()

    @validator("descricao_clausula")
    def valida_descricao_clausula(cls, value):
        cls.checa_vazio(value, "Descrição da Cláusula/Item")
        return value.strip()

    @validator("status")
    def valida_status(cls, value):
        cls.checa_vazio(value, "Status")
        return value.strip()


class ImportacaoPlanilhaTipoOcorrenciaSchema(BaseModel):
    posicao: Optional[str]
    perfis: Optional[str]
    edital: Optional[str]
    categoria_ocorrencia: Optional[str]
    titulo: Optional[str]
    descricao: Optional[str]
    penalidade: Optional[str]
    eh_imr: Optional[str]
    pontuacao: Optional[str]
    tolerancia: Optional[str]
    porcentagem_desconto: Optional[str]
    status: Optional[str]

    @classmethod
    def checa_vazio(cls, value, nome_parametro):
        if not value:
            raise Exception(f"{nome_parametro} não pode ser vazio.")

    @classmethod
    def eh_inteiro(cls, value, nome_parametro):
        if value and not value.is_digit():
            raise Exception(f"{nome_parametro} deve ser um número inteiro positivo.")

    @validator("posicao")
    def valida_posicao(cls, value):
        cls.checa_vazio(value, "Posição")
        cls.eh_inteiro(value, "Posição")
        return value.strip()

    @validator("perfis")
    def valida_perfis(cls, value):
        cls.checa_vazio(value, "Perfis")
        return value.strip()

    @validator("edital")
    def valida_edital(cls, value):
        cls.checa_vazio(value, "Edital")
        return value.strip()

    @validator("categoria_ocorrencia")
    def valida_categoria_ocorrencia(cls, value):
        cls.checa_vazio(value, "Categoria da Ocorrência")
        return value.strip()

    @validator("titulo")
    def valida_titulo(cls, value):
        cls.checa_vazio(value, "Titulo")
        return value.strip()

    @validator("descricao")
    def valida_descricao(cls, value):
        cls.checa_vazio(value, "Descrição")
        return value.strip()

    @validator("penalidade")
    def valida_penalidade(cls, value):
        cls.checa_vazio(value, "Penalidade")
        return value.strip()

    @validator("eh_imr")
    def valida_eh_imr(cls, value):
        cls.checa_vazio(value, "É IMR?")
        return value.strip()

    @validator("pontuacao")
    def valida_pontuacao(cls, value):
        cls.eh_inteiro(value, "Pontuação (IMR)")
        return value.strip()

    @validator("tolerancia")
    def valida_tolerancia(cls, value):
        cls.eh_inteiro(value, "Tolerância")
        return value.strip()

    @validator("porcentagem_desconto")
    def valida_porcentagem_desconto(cls, value):
        cls.checa_vazio(value, "% de Desconto")
        return value.strip()

    @validator("status")
    def valida_status(cls, value):
        cls.checa_vazio(value, "Status")
        return value.strip()
