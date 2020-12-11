from ...dados_comuns.fluxo_status import HomologacaoProdutoWorkflow


NOVA_RECLAMACAO_HOMOLOGACOES_STATUS = [
    HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO,
    HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
    HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
    HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO
]
