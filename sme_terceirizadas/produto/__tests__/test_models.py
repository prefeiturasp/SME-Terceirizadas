from datetime import datetime, timedelta

import pytest

pytestmark = pytest.mark.django_db


def test_homologacao_produto_tempo_aguardando_acao_em_dias(homologacao_produto, user):
    homologacao_produto.inicia_fluxo(user=user)
    log = homologacao_produto.logs.first()
    log.criado_em = datetime.today() - timedelta(days=5)
    log.save()
    assert homologacao_produto.tempo_aguardando_acao_em_dias == 5
    homologacao_produto.codae_homologa(user=user, link_pdf='')
    assert homologacao_produto.tempo_aguardando_acao_em_dias == 5
