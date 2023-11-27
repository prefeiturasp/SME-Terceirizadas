import datetime

import pytest

from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ...terceirizada.models import Edital
from ..models import SolicitacaoDietaEspecial
from ..utils import (
    dietas_especiais_a_terminar,
    gera_logs_dietas_escolas_cei,
    gera_logs_dietas_escolas_comuns,
    termina_dietas_especiais
)


@pytest.mark.django_db
def test_dietas_especiais_a_terminar(solicitacoes_dieta_especial_com_data_termino):
    assert dietas_especiais_a_terminar().count() == 3


@pytest.mark.django_db
def test_termina_dietas_especiais(solicitacoes_dieta_especial_com_data_termino, usuario_admin):
    termina_dietas_especiais(usuario_admin)
    assert dietas_especiais_a_terminar().count() == 0
    assert SolicitacaoDietaEspecial.objects.filter(
        status=DietaEspecialWorkflow.TERMINADA_AUTOMATICAMENTE_SISTEMA).count() == 3


@pytest.mark.django_db
def test_registrar_historico_criacao(protocolo_padrao_dieta_especial_2, substituicao_padrao_dieta_especial_2):
    from ..utils import log_create

    log_create(protocolo_padrao_dieta_especial_2)
    assert protocolo_padrao_dieta_especial_2.historico


@pytest.mark.django_db
def test_diff_protocolo_padrao(protocolo_padrao_dieta_especial_2, substituicao_padrao_dieta_especial_2, edital):
    from ..utils import diff_protocolo_padrao
    validated_data = {
        'nome_protocolo': 'Alergia a manga',
        'orientacoes_gerais': 'Uma orientação',
        'status': 'I',
        'editais': [edital.uuid]
    }
    old_editais = protocolo_padrao_dieta_especial_2.editais
    new_editais = validated_data.get('editais')
    new_editais = Edital.objects.filter(uuid__in=new_editais)
    changes = diff_protocolo_padrao(protocolo_padrao_dieta_especial_2, validated_data, old_editais, old_editais)
    assert changes


@pytest.mark.django_db
def test_gera_logs_dietas_escolas_comuns(escola, solicitacoes_dieta_especial_ativas):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    logs = gera_logs_dietas_escolas_comuns(escola, solicitacoes_dieta_especial_ativas, ontem)
    assert len(logs) == 6
    assert len([log for log in logs if log.classificacao.nome == 'Tipo A']) == 2


@pytest.mark.django_db
def test_gera_logs_dietas_escolas_cei(escola_cei, solicitacoes_dieta_especial_ativas_cei):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    logs = gera_logs_dietas_escolas_cei(escola_cei, solicitacoes_dieta_especial_ativas_cei, ontem)
    assert len(logs) == 2
    assert len([log for log in logs if log.classificacao.nome == 'Tipo A']) == 1
    assert [log for log in logs if log.classificacao.nome == 'Tipo A'][0].quantidade == 2


@pytest.mark.django_db
def test_gera_logs_dietas_escolas_cemei(escola_cemei, solicitacoes_dieta_especial_ativas_cemei):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    logs = gera_logs_dietas_escolas_comuns(escola_cemei, solicitacoes_dieta_especial_ativas_cemei, ontem)
    assert len(logs) == 12
    assert [log for log in logs if log.cei_ou_emei == 'N/A' and log.classificacao.nome == 'Tipo A'][0].quantidade == 3
    assert [log for log in logs if log.cei_ou_emei == 'CEI' and log.classificacao.nome == 'Tipo A'][0].quantidade == 2
    assert [log for log in logs if log.cei_ou_emei == 'EMEI' and log.classificacao.nome == 'Tipo A'][0].quantidade == 1


@pytest.mark.django_db
def test_gera_logs_dietas_escolas_cei_com_solicitacao_medicao(
    escola_cei,
    solicitacoes_dieta_especial_ativas_cei_com_solicitacao_medicao
):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    logs = gera_logs_dietas_escolas_cei(
        escola_cei, solicitacoes_dieta_especial_ativas_cei_com_solicitacao_medicao, ontem)
    assert len(logs) == 3
    assert len([log for log in logs if log.classificacao.nome == 'Tipo B']) == 1
    assert [log for log in logs if log.classificacao.nome == 'Tipo A Enteral'][0].quantidade == 1
    assert [log for log in logs if log.classificacao.nome == 'Tipo B'][0].quantidade == 2
