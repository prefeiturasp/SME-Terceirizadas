
from unittest.mock import patch

import pytest
from rest_framework import status

from sme_terceirizadas.perfil.models import ImportacaoPlanilhaUsuarioExternoCoreSSO

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_processar_planilha_externo_coresso(client_autenticado_dilog, planilha_usuario_externo, arquivo_xls):
    assert ImportacaoPlanilhaUsuarioExternoCoreSSO.objects.get(uuid=planilha_usuario_externo.uuid).status == 'PENDENTE'
    api_cria_ou_atualiza_usuario_core_sso = 'sme_terceirizadas.perfil.services.usuario_coresso_service.EOLUsuarioCoreSSO.cria_ou_atualiza_usuario_core_sso'  # noqa
    with patch(api_cria_ou_atualiza_usuario_core_sso):
        response = client_autenticado_dilog.post(
            f'/planilha-coresso-externo/{planilha_usuario_externo.uuid}/processar-importacao/')
    assert response.status_code == status.HTTP_200_OK
    import time
    time.sleep(10)  # Aguardar a task rodar.
    assert ImportacaoPlanilhaUsuarioExternoCoreSSO.objects.get(uuid=planilha_usuario_externo.uuid).status == 'SUCESSO'
