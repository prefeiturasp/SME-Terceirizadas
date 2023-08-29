import pytest

from sme_terceirizadas.pre_recebimento.utils import ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles

pytestmark = pytest.mark.django_db


def test_service_dashboard_solicitacao_alteracao_cronograma_profiles(
    django_user_model,
    client_autenticado_dinutre_diretoria
):
    service = ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles()
    usuario = django_user_model.objects.first()
    status_esperados = [
        'CRONOGRAMA_CIENTE',
        'APROVADO_DINUTRE',
        'REPROVADO_DINUTRE',
    ]

    assert service.get_dashboard_status(usuario) == status_esperados


def test_service_dashboard_solicitacao_alteracao_cronograma_profiles_value_error(
    django_user_model,
    client_autenticado_vinculo_escola
):
    service = ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles()
    usuario = django_user_model.objects.first()

    with pytest.raises(ValueError, match='Perfil não existe'):
        service.get_dashboard_status(usuario)
