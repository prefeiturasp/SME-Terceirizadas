import pytest

from sme_terceirizadas.recebimento.models import QuestaoConferencia

pytestmark = pytest.mark.django_db


def test_questao_conferencia_instance_model(questao_conferencia_factory):
    questao_conferencia = questao_conferencia_factory.create()
    assert isinstance(questao_conferencia, QuestaoConferencia)


def test_questao_conferencia_srt_model(questao_conferencia_factory):
    questao_conferencia = questao_conferencia_factory.create(
        questao="IDENTIFICACÃO DO PRODUTO"
    )
    assert questao_conferencia.__str__() == "IDENTIFICACÃO DO PRODUTO"


def test_questao_conferencia_meta_modelo(questao_conferencia_factory):
    questao_conferencia = questao_conferencia_factory.create()
    assert questao_conferencia._meta.verbose_name == "Questão para Conferência"
    assert questao_conferencia._meta.verbose_name_plural == "Questões para Conferência"
