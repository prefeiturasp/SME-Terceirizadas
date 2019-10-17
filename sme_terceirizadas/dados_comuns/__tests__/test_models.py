import pytest
from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_template_mensagem(template_mensagem):
    params, esperado = template_mensagem
    template = mommy.make(**params)
    assert isinstance(template.assunto, str)
    assert isinstance(template.template_html, str)
