from django_xworkflows import models as xwf_models


class PedidoAPartirDaEscolaWorkflow(xwf_models.Workflow):
    # leia com atenção: https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    DRE_A_VALIDAR = 'DRE_A_VALIDAR'
    DRE_APROVADO = 'DRE_APROVADO'
    DRE_PEDE_ESCOLA_REVISAR = 'DRE_PEDE_ESCOLA_REVISAR'  # PODE HAVER LOOP AQUI...
    CODAE_APROVADO = 'CODAE_APROVADO'
    CODAE_RECUSOU = 'CODAE_APROVADO'  # FIM, NOTIFICA ESCOLA E DRE
    TERCEIRIZADA_TOMA_CIENCIA = 'CODAE_APROVADO'  # FIM, NOTIFICA ESCOLA, DRE E CODAE

    states = (
        (RASCUNHO, "Rascunho"),
        (DRE_A_VALIDAR, "DRE a validar"),
        (DRE_APROVADO, "DRE aprovado"),
        (DRE_PEDE_ESCOLA_REVISAR, "Escola tem que revisar o pedido"),
        (CODAE_APROVADO, "CODAE aprovado"),
        (CODAE_RECUSOU, "CODAE recusa"),
        (TERCEIRIZADA_TOMA_CIENCIA, "Terceirizada toma ciencia"),
    )
    transitions = (
        ('comeca_fluxo', RASCUNHO, DRE_A_VALIDAR),
        ('dre_aprovou', DRE_A_VALIDAR, DRE_APROVADO),
        ('dre_pediu_revisao', DRE_A_VALIDAR, DRE_PEDE_ESCOLA_REVISAR),
        ('escola_revisou', DRE_PEDE_ESCOLA_REVISAR, DRE_A_VALIDAR),
        ('codae_aprovou', DRE_APROVADO, CODAE_APROVADO),
        ('codae_recusou', DRE_APROVADO, CODAE_RECUSOU),
        ('terceirizada_toma_ciencia', CODAE_APROVADO, TERCEIRIZADA_TOMA_CIENCIA),
    )

    initial_state = RASCUNHO
