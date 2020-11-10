import pytest
from django.contrib.auth import get_user_model

from sme_terceirizadas.logistica.models.guia import Guia

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_instance_model(solicitacao, guia):
    assert isinstance(guia, Guia)


def test_srt_model(guia):
    assert guia.__str__() == 'Guia: 987654 - INTEGRADA da solicitação: 559890'


def test_meta_modelo(guia):
    assert guia._meta.verbose_name == 'Guia de Remessa'
    assert guia._meta.verbose_name_plural == 'Guias de Remessas'
