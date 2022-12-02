import pytest

from ..models import Cronograma, EmbalagemQld, EtapasDoCronograma, Laboratorio, ProgramacaoDoRecebimentoDoCronograma

pytestmark = pytest.mark.django_db


def test_cronograma_instance_model(cronograma):
    assert isinstance(cronograma, Cronograma)


def test_cronograma_srt_model(cronograma):
    assert cronograma.__str__() == 'Cronograma: 001/2022 - Status: Rascunho'


def test_cronograma_meta_modelo(cronograma):
    assert cronograma._meta.verbose_name == 'Cronograma'
    assert cronograma._meta.verbose_name_plural == 'Cronogramas'


def test_etapas_do_cronograma_instance_model(etapa):
    assert isinstance(etapa, EtapasDoCronograma)


def test_etapas_do_cronograma_srt_model(etapa):
    assert etapa.__str__() == 'Etapa 1 do cronogrma 001/2022'


def test_etapas_do_cronograma_meta_modelo(etapa):
    assert etapa._meta.verbose_name == 'Etapa do Cronograma'
    assert etapa._meta.verbose_name_plural == 'Etapas dos Cronogramas'


def test_programacao_de_recebimento_do_cronograma_instance_model(programacao):
    assert isinstance(programacao, ProgramacaoDoRecebimentoDoCronograma)


def test_programacao_de_recebimento_do_cronograma_srt_model(programacao):
    assert programacao.__str__() == '01/01/2022'


def test_programacao_de_recebimento_do_cronograma_meta_modelo(programacao):
    assert programacao._meta.verbose_name == 'Programação do Recebimento do Cromograma'
    assert programacao._meta.verbose_name_plural == 'Programações dos Recebimentos dos Cromogramas'


def test_laboratorio_instance_model(laboratorio):
    assert isinstance(laboratorio, Laboratorio)


def test_laboratorio_srt_model(laboratorio):
    assert laboratorio.__str__() == 'Labo Test'


def test_laboratorio_meta_modelo(laboratorio):
    assert laboratorio._meta.verbose_name == 'Laboratório'
    assert laboratorio._meta.verbose_name_plural == 'Laboratórios'


def test_embalagem_instance_model(emabalagem_qld):
    assert isinstance(emabalagem_qld, EmbalagemQld)


def test_embalagem_srt_model(emabalagem_qld):
    assert emabalagem_qld.__str__() == 'CAIXA'


def test_embalagem_meta_modelo(emabalagem_qld):
    assert emabalagem_qld._meta.verbose_name == 'Embalagem QLD'
    assert emabalagem_qld._meta.verbose_name_plural == 'Embalagens QLD'
