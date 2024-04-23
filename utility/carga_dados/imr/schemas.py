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
