from ...dados_comuns.models import LogSolicitacoesUsuario


def test_aceita_nao_aceita_str():
    from ..templatetags.index import aceita_nao_aceita_str  # XXX: bug no teste de template nao registrado
    assert aceita_nao_aceita_str(False) == 'Não aceitou'
    assert aceita_nao_aceita_str(True) == 'Aceitou'


def test_class_css():
    from ..templatetags.index import class_css  # XXX: bug no teste de template nao registrado
    status_dic = dict((x, y) for x, y in LogSolicitacoesUsuario.STATUS_POSSIVEIS)

    class FakeSolicitacao():
        def __init__(self, status_evento_explicacao):
            self.status_evento_explicacao = status_evento_explicacao

    solicitacao_terc_quest = FakeSolicitacao(
        status_dic.get(LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO))
    solicitacao_dre_revisou = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.DRE_REVISOU))
    solicitacao_codae_aut = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.CODAE_AUTORIZOU))
    solicitacao_codae_neg_intv = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.CODAE_NEGOU_INATIVACAO))
    solicitacao_codae_neg = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.CODAE_NEGOU))
    solicitacao_escola_canc = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.ESCOLA_CANCELOU))
    solicitacao_codae_quest = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.CODAE_QUESTIONOU))

    assert class_css(solicitacao_terc_quest) == 'pending'
    assert class_css(solicitacao_dre_revisou) == 'active'
    assert class_css(solicitacao_codae_aut) == 'active'
    assert class_css(solicitacao_codae_neg_intv) == 'disapproved'
    assert class_css(solicitacao_codae_neg) == 'disapproved'
    assert class_css(solicitacao_escola_canc) == 'cancelled'
    assert class_css(solicitacao_codae_quest) == 'questioned'


def test_fim_de_fluxo():
    from ..templatetags.index import fim_de_fluxo  # XXX: bug no teste de template nao registrado
    status_dic = dict((x, y) for x, y in LogSolicitacoesUsuario.STATUS_POSSIVEIS)

    class FakeSolicitacao():
        def __init__(self, status_evento_explicacao):
            self.status_evento_explicacao = status_evento_explicacao

    solicitacao_codae_negado = FakeSolicitacao(
        status_dic.get(LogSolicitacoesUsuario.CODAE_NEGOU))
    solicitacao_dre_revisou = FakeSolicitacao(status_dic.get(LogSolicitacoesUsuario.DRE_REVISOU))
    assert fim_de_fluxo([solicitacao_codae_negado]) is True
    assert fim_de_fluxo([solicitacao_dre_revisou]) is False
