import pytest
from model_mommy import mommy

from .. import models


@pytest.fixture
def perfil():
    return mommy.make(models.Perfil, nome='título do perfil')

#
# @pytest.fixture
# def permission():
#     return mommy.make(Permissao, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')
#
#
# @pytest.fixture
# def profile_permission():
#     permission = mommy.make(Permissao, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')
#     return mommy.make(PermissaoPerfil, permission=permission)
