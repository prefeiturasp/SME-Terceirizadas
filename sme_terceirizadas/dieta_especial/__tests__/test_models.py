import pytest
import xworkflows

pytestmark = pytest.mark.django_db


def test_solicitacao_dieta_especial_obj(solicitacao_dieta_especial):
    assert solicitacao_dieta_especial.__str__() == '123456: Roberto Alves da Silva'
    assert solicitacao_dieta_especial.escola == solicitacao_dieta_especial.rastro_escola


def test_anexo_obj(anexo_docx):
    assert anexo_docx.nome == anexo_docx.nome


def test_termina_dieta_especial_erro_status_invalido(solicitacoes_dieta_especial_nao_autorizadas_e_nao_ativas,
                                                     usuario_admin):
    for solicitacao in solicitacoes_dieta_especial_nao_autorizadas_e_nao_ativas:
        try:
            solicitacao.termina(usuario_admin)
        except xworkflows.InvalidTransitionError as e:
            assert str(e) == 'Só é permitido terminar dietas autorizadas e ativas'


def test_termina_dieta_especial_erro_ativas_sem_dt_termino(solicitacao_dieta_especial_autorizada_ativa,
                                                           usuario_admin):
    try:
        solicitacao_dieta_especial_autorizada_ativa.termina(usuario_admin)
    except xworkflows.InvalidTransitionError as e:
        assert str(e) == 'Não pode terminar uma dieta sem data de término'


def test_termina_dieta_especial_erro_dt_termino_posterior_hoje(solicitacoes_dieta_especial_dt_termino_hoje_ou_posterior,
                                                               usuario_admin):
    for solicitacao in solicitacoes_dieta_especial_dt_termino_hoje_ou_posterior:
        try:
            solicitacao.termina(usuario_admin)
        except xworkflows.InvalidTransitionError as e:
            assert str(e) == 'Não pode terminar uma dieta antes da data'


def test_termina_dieta_especial_erro_dt_termino_no_passado(solicitacoes_dieta_especial_dt_termino_ontem,
                                                           usuario_admin):
    for solicitacao in solicitacoes_dieta_especial_dt_termino_ontem:
        solicitacao.termina(usuario_admin)
        ultimo_log = solicitacao.logs.last()
        assert ultimo_log.usuario_id == usuario_admin.id
        assert ultimo_log.justificativa == 'Atingiu data limite e foi terminada automaticamente'
