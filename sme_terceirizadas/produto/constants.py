from ..dados_comuns.fluxo_status import (
    HomologacaoProdutoWorkflow,
    ReclamacaoProdutoWorkflow,
)

NOVA_RECLAMACAO_HOMOLOGACOES_STATUS = [
    HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
    HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
    HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
    HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
]

AVALIAR_RECLAMACAO_HOMOLOGACOES_STATUS = [
    HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
    HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
    HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
    HomologacaoProdutoWorkflow.CODAE_AUTORIZOU_RECLAMACAO,
]

AVALIAR_RECLAMACAO_RECLAMACOES_STATUS = [
    ReclamacaoProdutoWorkflow.AGUARDANDO_AVALIACAO,
    ReclamacaoProdutoWorkflow.RESPONDIDO_TERCEIRIZADA,
]

RESPONDER_RECLAMACAO_HOMOLOGACOES_STATUS = [
    HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
    HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
]

RESPONDER_RECLAMACAO_RECLAMACOES_STATUS = [
    ReclamacaoProdutoWorkflow.AGUARDANDO_RESPOSTA_TERCEIRIZADA
]
