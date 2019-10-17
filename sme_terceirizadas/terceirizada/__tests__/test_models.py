import pytest

pytestmark = pytest.mark.django_db


def test_modelo_edital(edital):
    assert edital.uuid is not None
    assert edital.tipo_contratacao is not None
    assert edital.numero is not None
    assert edital.processo is not None
    assert edital.numero is not None
    assert edital.objeto is not None
    assert edital.contratos is not None


def test_modelo_contrato(contrato):
    assert contrato.uuid is not None
    assert contrato.numero is not None
    assert contrato.processo is not None
    assert contrato.data_proposta is not None
    assert contrato.lotes is not None
    assert contrato.terceirizada is not None
    assert contrato.vigencias is not None
    assert contrato.diretorias_regionais is not None


def test_modelo_vigencia_contrato(vigencia_contrato):
    assert vigencia_contrato.uuid is not None
    assert vigencia_contrato.data_inicial is not None
    assert vigencia_contrato.data_final is not None


def test_terceirizada(terceirizada):
    assert terceirizada.nutricionistas is not None
    assert terceirizada.inclusoes_continuas_autorizadas is not None
    assert terceirizada.inclusoes_normais_autorizadas is not None
    assert terceirizada.inclusoes_continuas_reprovadas is not None
    assert terceirizada.solicitacao_kit_lanche_avulsa_autorizadas is not None
    assert terceirizada.inclusoes_normais_reprovadas is not None
    assert terceirizada.alteracoes_cardapio_autorizadas is not None
    assert terceirizada.alteracoes_cardapio_reprovadas is not None
    assert terceirizada.inversoes_cardapio_autorizadas is not None
    assert terceirizada.solicitacoes_unificadas_autorizadas is not None

    filtro = 'Hoje'
    assert terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(filtro) is not None
    assert terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_limite(filtro) is not None
    assert terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_regular(filtro) is not None
    assert terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_vencendo(filtro) is not None
    assert terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_limite(filtro) is not None
    assert terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_regular(filtro) is not None
    assert terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_vencendo(filtro) is not None
    assert terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_limite(filtro) is not None
    assert terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_regular(filtro) is not None
    assert terceirizada.alteracoes_cardapio_das_minhas(filtro) is not None
    assert terceirizada.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(filtro) is not None
    assert terceirizada.inclusoes_alimentacao_continua_das_minhas_escolas(filtro) is not None
    assert terceirizada.suspensoes_alimentacao_das_minhas_escolas(filtro) is not None
    assert terceirizada.inversoes_cardapio_das_minhas_escolas(filtro) is not None
    assert terceirizada.solicitacoes_unificadas_das_minhas_escolas(filtro) is not None
    assert terceirizada.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(filtro) is not None
