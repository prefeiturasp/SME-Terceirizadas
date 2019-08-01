import pytest
from model_mommy import mommy

pytestmark = pytest.mark.django_db


class FakeModel(object):
    id_externo = 'FAKE_id_externo'
    criado_em = 'FAKE_criado_em'
    criado_por = 'FAKE_criado_por'
    status = 'FAKE_status'
    data_inicial = 'FAKE_data_inicial'
    data_final = 'FAKE_data_final'


fake_model = FakeModel()


def test_template_mensagem(template_mensagem):
    params, esperado = template_mensagem
    template = mommy.make(**params)
    assert isinstance(template.assunto, str)
    assert isinstance(template.template_html, str)
    assert template.aplica_objeto_no_template(fake_model) == esperado
