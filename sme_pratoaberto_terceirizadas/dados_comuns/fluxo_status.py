"""Classes de apoio devem ser usadas em conjunto com as classes abstratas de fluxo.

Na pasta docs tem os BMPNs dos fluxos
"""
from django_xworkflows import models as xwf_models


class PedidoAPartirDaEscolaWorkflow(xwf_models.Workflow):
    # leia com atenção: https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    DRE_A_VALIDAR = 'DRE_A_VALIDAR'
    DRE_VALIDADO = 'DRE_VALIDADO'
    DRE_PEDIU_ESCOLA_REVISAR = 'DRE_PEDIU_ESCOLA_REVISAR'  # PODE HAVER LOOP AQUI...
    DRE_NAO_VALIDOU_PEDIDO_ESCOLA = 'DRE_NAO_VALIDOU_PEDIDO_ESCOLA'  # FIM DE FLUXO
    CODAE_AUTORIZADO = 'CODAE_AUTORIZADO'
    CODAE_NEGOU_PEDIDO = 'CODAE_NEGOU_PEDIDO'  # FIM, NOTIFICA ESCOLA E DRE
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMOU_CIENCIA'  # FIM, NOTIFICA ESCOLA, DRE E CODAE

    # UM STATUS POSSIVEL, QUE PODE SER ATIVADO PELA ESCOLA EM ATE X HORAS ANTES
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    ESCOLA_CANCELOU = 'ESCOLA_CANCELOU'

    # TEM UMA ROTINA QUE CANCELA CASO O PEDIDO TENHA PASSADO DO DIA E NÃO TENHA TERMINADO O FLUXO
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    CANCELADO_AUTOMATICAMENTE = 'CANCELADO_AUTOMATICAMENTE'

    states = (
        (RASCUNHO, 'Rascunho'),
        (DRE_A_VALIDAR, 'DRE a validar'),
        (DRE_VALIDADO, 'DRE validado'),
        (DRE_PEDIU_ESCOLA_REVISAR, 'Escola tem que revisar o pedido'),
        (DRE_NAO_VALIDOU_PEDIDO_ESCOLA, 'DRE não validou pedido da escola'),
        (CODAE_AUTORIZADO, 'CODAE autorizou pedido'),
        (CODAE_NEGOU_PEDIDO, 'CODAE negou pedido'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada tomou'),
        (ESCOLA_CANCELOU, 'Escola cancelou'),
        (CANCELADO_AUTOMATICAMENTE, 'Cancelamento automático'),
    )

    transitions = (
        ('inicia_fluxo', RASCUNHO, DRE_A_VALIDAR),
        ('dre_validou', DRE_A_VALIDAR, DRE_VALIDADO),
        ('dre_pediu_revisao', DRE_A_VALIDAR, DRE_PEDIU_ESCOLA_REVISAR),
        ('dre_nao_validou_pedido', DRE_A_VALIDAR, DRE_NAO_VALIDOU_PEDIDO_ESCOLA),
        ('escola_revisou', DRE_PEDIU_ESCOLA_REVISAR, DRE_A_VALIDAR),
        ('codae_autorizou', DRE_VALIDADO, CODAE_AUTORIZADO),
        ('codae_negou', DRE_VALIDADO, CODAE_NEGOU_PEDIDO),
        ('terceirizada_tomou_ciencia', CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA),
    )

    initial_state = RASCUNHO


class PedidoAPartirDaDiretoriaRegionalWorkflow(xwf_models.Workflow):
    # leia com atenção: https://django-xworkflows.readthedocs.io/en/latest/index.html

    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    CODAE_A_AUTORIZAR = 'CODAE_A_VALIDAR'
    CODAE_PEDIU_DRE_REVISAR = 'DRE_PEDE_ESCOLA_REVISAR'  # PODE HAVER LOOP AQUI...
    CODAE_NEGOU_PEDIDO = 'CODAE_CANCELOU_PEDIDO'  # FIM DE FLUXO
    CODAE_AUTORIZADO = 'CODAE_APROVADO'
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMA_CIENCIA'  # FIM, NOTIFICA ESCOLA, DRE E CODAE

    # UM STATUS POSSIVEL, QUE PODE SER ATIVADO PELA DRE EM ATE X HORAS ANTES
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    DRE_CANCELOU = 'DRE_CANCELOU'

    # TEM UMA ROTINA QUE CANCELA CASO O PEDIDO TENHA PASSADO DO DIA E NÃO TENHA TERMINADO O FLUXO
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    CANCELAMENTO_AUTOMATICO = 'CANCELAMENTO_AUTOMATICO'

    states = (
        (RASCUNHO, 'Rascunho'),
        (CODAE_A_AUTORIZAR, 'CODAE a autorizar'),
        (CODAE_PEDIU_DRE_REVISAR, 'DRE tem que revisar o pedido'),
        (CODAE_NEGOU_PEDIDO, 'CODAE negou o pedido da DRE'),
        (CODAE_AUTORIZADO, 'CODAE autorizou'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada tomou ciencia'),
        (CANCELAMENTO_AUTOMATICO, 'Cancelamento automático'),
        (DRE_CANCELOU, 'DRE cancelou'),
    )

    transitions = (
        ('inicia_fluxo', RASCUNHO, CODAE_A_AUTORIZAR),
        ('codae_pediu_revisao', CODAE_A_AUTORIZAR, CODAE_PEDIU_DRE_REVISAR),
        ('codae_negou', CODAE_A_AUTORIZAR, CODAE_NEGOU_PEDIDO),
        ('dre_revisou', CODAE_PEDIU_DRE_REVISAR, CODAE_A_AUTORIZAR),
        ('codae_autorizou', CODAE_A_AUTORIZAR, CODAE_AUTORIZADO),
        ('terceirizada_tomou_ciencia', CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA),
    )

    initial_state = RASCUNHO


class InformativoPartindoDaEscolaWorkflow(xwf_models.Workflow):
    # leia com atenção: https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    INFORMADO = 'INFORMADO'
    TERCEIRIZADA_TOMA_CIENCIA = 'TERCEIRIZADA_TOMA_CIENCIA'

    states = (
        (RASCUNHO, 'Rascunho'),
        (INFORMADO, 'Informado'),
        (TERCEIRIZADA_TOMA_CIENCIA, 'Terceirizada toma ciencia'),
    )

    transitions = (
        ('informa', RASCUNHO, INFORMADO),
        ('terceirizada_tomou_ciencia', INFORMADO, TERCEIRIZADA_TOMA_CIENCIA),
    )

    initial_state = RASCUNHO
