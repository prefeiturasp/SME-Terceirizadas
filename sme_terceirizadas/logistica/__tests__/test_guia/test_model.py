import pytest
from django.contrib.auth import get_user_model

from ...models.guia import ConferenciaGuia, Guia, InsucessoEntregaGuia

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_instance_model(solicitacao, guia):
    assert isinstance(guia, Guia)


def test_srt_model(guia):
    assert guia.__str__() == 'Guia: 987654 - AGUARDANDO_ENVIO da solicitação: 559890'


def test_meta_modelo(guia):
    assert guia._meta.verbose_name == 'Guia de Remessa'
    assert guia._meta.verbose_name_plural == 'Guias de Remessas'


def test_instance_conferencia_guia_model(conferencia_guia):
    assert isinstance(conferencia_guia, ConferenciaGuia)


def test_srt_conferencia_guiamodel(conferencia_guia):
    assert conferencia_guia.__str__() == 'Conferência da guia 987654'


def test_meta_conferencia_guiamodelo(conferencia_guia):
    assert conferencia_guia._meta.verbose_name == 'Conferência da Guia de Remessa'
    assert conferencia_guia._meta.verbose_name_plural == 'Conferência das Guias de Remessas'


def test_instance_insucesso_entrega_guia_model(insucesso_entrega_guia):
    assert isinstance(insucesso_entrega_guia, InsucessoEntregaGuia)


def test_srt_insucesso_entrega_guiamodel(insucesso_entrega_guia):
    assert insucesso_entrega_guia.__str__() == 'Insucesso de entrega da guia 987654'


def test_meta_insucesso_entrega_guiamodelo(insucesso_entrega_guia):
    assert insucesso_entrega_guia._meta.verbose_name == 'Insucesso de Entrega da Guia'
    assert insucesso_entrega_guia._meta.verbose_name_plural == 'Insucessos de Entregas das Guias'
