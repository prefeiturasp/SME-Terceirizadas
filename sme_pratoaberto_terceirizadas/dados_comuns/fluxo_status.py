from statemachine import StateMachine, State


class ControleDeFluxoDeStatusAPartirDaEscola(StateMachine):
    # https://python-statemachine.readthedocs.io/en/latest/readme.html
    RASCUNHO = 0  # INICIO
    DRE_A_VALIDAR = 1
    DRE_APROVADO = 2
    DRE_PEDE_REVISAO = 3  # PODE HAVER LOOP AQUI...
    CODAE_APROVADO = 4
    CODAE_SUSPENDEU = 5  # FIM, NOTIFICA ESCOLA E DRE
    TERCEIRIZADA_TOMA_CIENCIA = 6  # FIM, NOTIFICA ESCOLA, DRE E CODAE

    _rascunho = State('RASCUNHO', initial=True, value=RASCUNHO)
    _dre_a_validar = State('DRE_A_VALIDAR', value=DRE_A_VALIDAR)
    _dre_aprovado = State('DRE_APROVADO', value=DRE_APROVADO)
    _dre_pede_revisao = State('DRE_PEDE_REVISAO', value=DRE_PEDE_REVISAO)
    _codae_aprovado = State('CODAE_APROVADO', value=CODAE_APROVADO)
    _codae_suspendeu = State('CODAE_SUSPENDEU', value=CODAE_SUSPENDEU)
    _terceirizada_toma_ciencia = State('TERCEIRIZADA_TOMA_CIENCIA', value=TERCEIRIZADA_TOMA_CIENCIA)

    comeca_fluxo = _rascunho.to(_dre_a_validar)
    dre_aprovou = _dre_a_validar.to(_dre_aprovado)
    dre_pediu_revisao = _dre_a_validar.to(_dre_pede_revisao)
    escola_revisou = _dre_pede_revisao.to(_dre_a_validar)
    codae_aprovou = _dre_aprovado.to(_codae_aprovado)
    codae_recusou = _dre_aprovado.to(_codae_suspendeu)
    terceirizada_toma_ciencia = _codae_aprovado.to(_terceirizada_toma_ciencia)

    def on_comeca_fluxo(self):
        print('Começando fluxo, avisa dre')

    def on_dre_aprovou(self):
        print('DRE aprovou, avisa codae')

    def on_dre_pediu_revisao(self):
        print('Escola... hora de revisar')

    def on_escola_revisou(self):
        print('Escola revisou, manda novamente')

    def on_codae_aprovou(self):
        print('Codae aprovou, terceirizada deve atender, avisa terc, dre e escola')

    def on_codae_recusou(self):
        print('Codae recusou fim de fluxo')

    def on_terceirizada_toma_ciencia(self):
        print('terceirizada tomou ciencia! notifica todos!')
