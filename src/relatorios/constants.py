from src.dados_comuns.constants import ESCOLA_CANCELOU_LABEL

TITULO_SOLICITACAO_REALIZADA = "Solicitação Realizada"
TITULO_CODAE = "CODAE"
TITULO_ESCOLA_SOLICITOU_CANCELAMENTO = "Escola solicitou cancelamento"

FLUXO_PARTINDO_DRE = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_PARTINDO_ESCOLA = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "DRE", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "Terceirizada", "status": "", "criado_em": "", "usuario": None},
]

FLUXO_ALTERACAO_DE_CARDAPIO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "DRE", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_KIT_LANCHE_PASSEIO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "DRE", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_INCLUSAO_ALIMENTACAO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "DRE", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_INVERSAO_DIA_CARDAPIO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "DRE", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_INFORMATIVO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "Terceirizada", "status": "", "criado_em": "", "usuario": None},
]

FLUXO_SUSPENSAO_ALIMENTACAO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None}
]

FLUXO_DIETA_ESPECIAL = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_HOMOLOGACAO_PRODUTO = [
    {"titulo": "Empresa terceirizada", "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_DIETA_ESPECIAL_INATIVACAO_INCOMPLETO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
    {
        "titulo": TITULO_ESCOLA_SOLICITOU_CANCELAMENTO,
        "status": "",
        "criado_em": "",
        "usuario": None,
    },
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_DIETA_ESPECIAL_INATIVACAO = [
    {"titulo": TITULO_SOLICITACAO_REALIZADA, "status": "", "criado_em": "", "usuario": None},
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
    {"titulo": "Terceirizada", "status": "", "criado_em": "", "usuario": None},
    {
        "titulo": TITULO_ESCOLA_SOLICITOU_CANCELAMENTO,
        "status": "",
        "criado_em": "",
        "usuario": None,
    },
    {"titulo": TITULO_CODAE, "status": "", "criado_em": "", "usuario": None},
]

FLUXO_DIETA_ESPECIAL_INATIVACAO_CANCELADO = [
    {
        "titulo": TITULO_ESCOLA_SOLICITOU_CANCELAMENTO,
        "status": "",
        "criado_em": "",
        "usuario": None,
    },
    {
        "titulo": ESCOLA_CANCELOU_LABEL,
        "status": "",
        "criado_em": "",
        "usuario": None,
    },
]
