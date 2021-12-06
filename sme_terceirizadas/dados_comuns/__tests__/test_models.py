import pytest
from model_mommy import mommy
from django.contrib import admin
from django.contrib.auth import get_user_model
from ..models import Notificacao

pytestmark = pytest.mark.django_db

User = get_user_model()

def test_template_mensagem(template_mensagem):
    params, esperado = template_mensagem
    template = mommy.make(**params)
    assert isinstance(template.assunto, str)
    assert isinstance(template.template_html, str)


def test_template_mensagem_obj(template_mensagem_obj):
    assert template_mensagem_obj.__str__() == 'Alteração do tipo de Alimentação'


def test_instance_model_notificacao(notificacao):
    model = notificacao
    assert isinstance(model, Notificacao)
    assert model.titulo
    assert model.descricao
    assert model.tipo
    assert model.categoria
    assert model.criado_em
    assert model.uuid
    assert isinstance(model.usuario, User)
    assert model.id


def test_srt_model_notificacao(notificacao):
    assert str(notificacao) == 'Nova requisição de entrega'


def test_meta_modelo_notificacao(notificacao):
    assert notificacao._meta.verbose_name == 'Notificação'
    assert notificacao._meta.verbose_name_plural == 'Notificações'


def test_admin_notificacao():
    assert admin.site._registry[Notificacao]
