from ..models import SolicitacaoMedicaoInicial

STATUS_RELACAO_DRE_UE = [
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_ENVIADA_PELA_UE,
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA,
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRIGIDA_PELA_UE
]

STATUS_RELACAO_DRE_CODAE = [
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_DRE,
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA_CODAE,
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRIGIDA_PARA_CODAE,
    SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_CODAE
]
