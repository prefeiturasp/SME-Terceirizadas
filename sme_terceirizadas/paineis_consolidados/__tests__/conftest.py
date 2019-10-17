import pytest
from model_mommy import mommy

from ...cardapio.models import AlteracaoCardapio


@pytest.fixture
def client_autenticado_painel_consolidados(client_autenticado, django_user_model):

    user = django_user_model.objects.get(email='test@test.com')
    diretoria_regional = mommy.make('escola.DiretoriaRegional',
                                    usuarios=[user],
                                    make_m2m=True
                                    )
    escola = mommy.make('escola.Escola', diretoria_regional=diretoria_regional)
    mommy.make(AlteracaoCardapio,
               escola=escola,
               status=AlteracaoCardapio.workflow_class.DRE_A_VALIDAR)
    return client_autenticado
