import datetime

import pytest
from freezegun import freeze_time
from model_mommy import mommy
from xworkflows import InvalidTransitionError

from ...dados_comuns.models_abstract import TempoPasseio

pytestmark = pytest.mark.django_db


def test_kit_lanche(kit_lanche):
    assert isinstance(kit_lanche.nome, str)
    assert isinstance(kit_lanche.__str__(), str)
    assert kit_lanche.itens.count() == 3
    assert kit_lanche._meta.verbose_name == 'Kit lanche'
    assert kit_lanche._meta.verbose_name_plural == 'Kit lanches'


def test_item_kit_lanche(item_kit_lanche):
    assert isinstance(item_kit_lanche.nome, str)
    assert isinstance(item_kit_lanche.__str__(), str)


def test_solicitacao_avulsa(solicitacao_avulsa):
    assert isinstance(solicitacao_avulsa.local, str)
    assert solicitacao_avulsa.quantidade_alunos == 999
    assert solicitacao_avulsa.quantidade_alimentacoes == 2997
    assert solicitacao_avulsa.data == datetime.datetime(2000, 1, 1)
    assert 'Solicitação' in solicitacao_avulsa._meta.verbose_name


def test_solicitacao_unificada(solicitacao_unificada_lista_igual):
    assert isinstance(solicitacao_unificada_lista_igual.local, str)
    assert solicitacao_unificada_lista_igual.lista_kit_lanche_igual is True

    escolas_quantidades = mommy.make('EscolaQuantidade', _quantity=10, quantidade_alunos=100)
    assert solicitacao_unificada_lista_igual.vincula_escolas_quantidades(
        escolas_quantidades) is None
    assert solicitacao_unificada_lista_igual.total_kit_lanche == 3000


def test_solicitacao_unificada_lotes_diferentes(solicitacao_unificada_lotes_diferentes):
    assert solicitacao_unificada_lotes_diferentes.quantidade_de_lotes == 2
    solicitacoes_unificadas = solicitacao_unificada_lotes_diferentes.dividir_por_lote()
    assert solicitacoes_unificadas.__len__() == 2


def test_solicitacao_unificada_lotes_iguais(solicitacao_unificada_lotes_iguais):
    assert solicitacao_unificada_lotes_iguais.quantidade_de_lotes == 1
    solicitacoes_unificadas = solicitacao_unificada_lotes_iguais.dividir_por_lote()
    assert solicitacoes_unificadas.__len__() == 1


def test_solicitacao(solicitacao):
    assert solicitacao.tempo_passeio == TempoPasseio.CINCO_A_SETE
    assert solicitacao.kits.count() == 3
    assert 'Solicitação kit lanche base' in solicitacao._meta.verbose_name


def test_solicitacao_avulsa_workflow_case_1_partindo_da_escola(solicitacao_avulsa):
    """RASCUNHO > DRE_A_VALIDAR > DRE_VALIDADO > CODAE_AUTORIZADO > TERCEIRIZADA_TOMOU_CIENCIA."""
    wc = solicitacao_avulsa.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_avulsa.status == wc.RASCUNHO

    solicitacao_avulsa.inicia_fluxo(user=user)
    assert solicitacao_avulsa.status == wc.DRE_A_VALIDAR

    solicitacao_avulsa.dre_valida(user=user, )
    assert solicitacao_avulsa.status == wc.DRE_VALIDADO

    solicitacao_avulsa.codae_autoriza(user=user, )
    assert solicitacao_avulsa.status == wc.CODAE_AUTORIZADO

    solicitacao_avulsa.terceirizada_toma_ciencia(user=user, )
    assert solicitacao_avulsa.status == wc.TERCEIRIZADA_TOMOU_CIENCIA


def test_solicitacao_avulsa_workflow_case_2_partindo_da_escola(solicitacao_avulsa):
    """RASCUNHO > DRE_A_VALIDAR > DRE_PEDIU_ESCOLA_REVISAR > DRE_A_VALIDAR."""
    wc = solicitacao_avulsa.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_avulsa.status == wc.RASCUNHO

    solicitacao_avulsa.inicia_fluxo(user=user)
    assert solicitacao_avulsa.status == wc.DRE_A_VALIDAR

    solicitacao_avulsa.dre_pede_revisao(user=user, )
    assert solicitacao_avulsa.status == wc.DRE_PEDIU_ESCOLA_REVISAR

    solicitacao_avulsa.escola_revisa(user=user, )
    assert solicitacao_avulsa.status == wc.DRE_A_VALIDAR


def test_solicitacao_avulsa_workflow_case_3_partindo_da_escola(solicitacao_avulsa):
    """RASCUNHO > DRE_A_VALIDAR > DRE_NAO_VALIDOU_PEDIDO_ESCOLA."""
    wc = solicitacao_avulsa.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_avulsa.status == wc.RASCUNHO

    solicitacao_avulsa.inicia_fluxo(user=user)
    assert solicitacao_avulsa.status == wc.DRE_A_VALIDAR

    solicitacao_avulsa.dre_nao_valida(user=user)
    assert solicitacao_avulsa.status == wc.DRE_NAO_VALIDOU_PEDIDO_ESCOLA


def test_solicitacao_avulsa_workflow_case_4_partindo_da_escola(solicitacao_avulsa):
    """RASCUNHO > DRE_A_VALIDAR > DRE_VALIDADO > CODAE_NEGOU_PEDIDO."""
    wc = solicitacao_avulsa.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_avulsa.status == wc.RASCUNHO

    solicitacao_avulsa.inicia_fluxo(user=user)
    assert solicitacao_avulsa.status == wc.DRE_A_VALIDAR

    solicitacao_avulsa.dre_valida(user=user, )
    assert solicitacao_avulsa.status == wc.DRE_VALIDADO

    solicitacao_avulsa.codae_nega(user=user)
    assert solicitacao_avulsa.status == wc.CODAE_NEGOU_PEDIDO


def test_solicitacao_avulsa_workflow_partindo_da_escola_with_error(solicitacao_avulsa):
    wc = solicitacao_avulsa.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_avulsa.status == wc.RASCUNHO

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_valida' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.dre_valida(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_nao_valida' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.dre_nao_valida(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_pede_revisao' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.dre_pede_revisao(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'codae_autoriza' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.codae_autoriza(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'codae_nega' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.codae_nega(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'terceirizada_toma_ciencia' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.terceirizada_toma_ciencia(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'escola_revisa' isn't available from state 'RASCUNHO'"):
        solicitacao_avulsa.escola_revisa(user=user)


def test_solicitacao_unificada_lista_igual_workflow_case_1_partindo_da_diretoria_regional(
    solicitacao_unificada_lista_igual
):
    """RASCUNHO > CODAE_A_AUTORIZAR > CODAE_PEDIU_DRE_REVISAR > CODAE_A_AUTORIZAR."""
    wc = solicitacao_unificada_lista_igual.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_unificada_lista_igual.status == wc.RASCUNHO

    solicitacao_unificada_lista_igual.inicia_fluxo(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_A_AUTORIZAR

    solicitacao_unificada_lista_igual.codae_pede_revisao(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_PEDIU_DRE_REVISAR

    solicitacao_unificada_lista_igual.dre_revisa(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_A_AUTORIZAR


def test_solicitacao_unificada_lista_igual_workflow_case_2_partindo_da_diretoria_regional(
    solicitacao_unificada_lista_igual
):
    """RASCUNHO > CODAE_A_AUTORIZAR > CODAE_AUTORIZADO > TERCEIRIZADA_TOMOU_CIENCIA."""
    wc = solicitacao_unificada_lista_igual.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_unificada_lista_igual.status == wc.RASCUNHO

    solicitacao_unificada_lista_igual.inicia_fluxo(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_A_AUTORIZAR

    solicitacao_unificada_lista_igual.codae_autoriza(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_AUTORIZADO

    solicitacao_unificada_lista_igual.terceirizada_toma_ciencia(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.TERCEIRIZADA_TOMOU_CIENCIA


def test_solicitacao_unificada_lista_igual_workflow_case_3_partindo_da_diretoria_regional(
    solicitacao_unificada_lista_igual
):
    """RASCUNHO > CODAE_A_AUTORIZAR > CODAE_NEGOU_PEDIDO."""
    wc = solicitacao_unificada_lista_igual.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_unificada_lista_igual.status == wc.RASCUNHO

    solicitacao_unificada_lista_igual.inicia_fluxo(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_A_AUTORIZAR

    solicitacao_unificada_lista_igual.codae_nega(user=user)
    assert solicitacao_unificada_lista_igual.status == wc.CODAE_NEGOU_PEDIDO


def test_solicitacao_unificada_lista_igual_workflow_partindo_da_escola_with_error(
    solicitacao_unificada_lista_igual
):
    wc = solicitacao_unificada_lista_igual.workflow_class
    user = mommy.make('perfil.Usuario')
    assert solicitacao_unificada_lista_igual.status == wc.RASCUNHO

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'codae_pede_revisao' isn't available from state 'RASCUNHO'"):
        solicitacao_unificada_lista_igual.codae_pede_revisao(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'codae_nega' isn't available from state 'RASCUNHO'"):
        solicitacao_unificada_lista_igual.codae_nega(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'dre_revisa' isn't available from state 'RASCUNHO'"):
        solicitacao_unificada_lista_igual.dre_revisa(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'codae_autoriza' isn't available from state 'RASCUNHO'"):
        solicitacao_unificada_lista_igual.codae_autoriza(user=user)

    with pytest.raises(InvalidTransitionError,
                       match="Transition 'terceirizada_toma_ciencia' isn't available from state 'RASCUNHO'"):
        solicitacao_unificada_lista_igual.terceirizada_toma_ciencia(user=user)


@freeze_time('2019-10-02')
def test_tageamento_prioridade(kits_avulsos_parametros):
    data_tupla, esperado = kits_avulsos_parametros
    kit_lanche_base = mommy.make('SolicitacaoKitLanche', data=datetime.date(*data_tupla))
    kit_lanche_avulso = mommy.make('SolicitacaoKitLancheAvulsa', solicitacao_kit_lanche=kit_lanche_base)
    assert kit_lanche_avulso.prioridade == esperado


@freeze_time('2019-12-20')
def test_tageamento_prioridade_caso2(kits_avulsos_parametros2):
    data_tupla, esperado = kits_avulsos_parametros2
    kit_lanche_base = mommy.make('SolicitacaoKitLanche', data=datetime.date(*data_tupla))
    kit_lanche_avulso = mommy.make('SolicitacaoKitLancheAvulsa', solicitacao_kit_lanche=kit_lanche_base)
    assert kit_lanche_avulso.prioridade == esperado
