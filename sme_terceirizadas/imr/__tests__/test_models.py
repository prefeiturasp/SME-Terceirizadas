import pytest

from sme_terceirizadas.imr.admin import FaixaPontuacaoIMRForm, TipoOcorrenciaForm
from sme_terceirizadas.imr.models import TipoOcorrencia, TipoPenalidade

pytestmark = pytest.mark.django_db


def test_tipo_penalidade_instance_model(tipo_penalidade_factory):
    tipo_penalidade = tipo_penalidade_factory.create()
    assert isinstance(tipo_penalidade, TipoPenalidade)


def test_tipo_penalidade_srt_model(tipo_penalidade_factory, edital_factory):
    edital = edital_factory.create(numero="SME/01/24")
    tipo_penalidade = tipo_penalidade_factory.create(
        numero_clausula="1.1.16", edital=edital
    )
    assert tipo_penalidade.__str__() == "Item: 1.1.16 - Edital: SME/01/24"


def test_tipo_penalidade_meta_modelo(tipo_penalidade_factory):
    tipo_penalidade = tipo_penalidade_factory.create()
    assert tipo_penalidade._meta.verbose_name == "Tipo de Penalidade"
    assert tipo_penalidade._meta.verbose_name_plural == "Tipos de Penalidades"


def test_tipo_ocorrencia_instance_model(tipo_ocorrencia_factory):
    tipo_ocorrencia = tipo_ocorrencia_factory.create()
    assert isinstance(tipo_ocorrencia, TipoOcorrencia)


def test_tipo_ocorrencia_srt_model(tipo_ocorrencia_factory, edital_factory):
    edital = edital_factory.create(numero="SME/02/24")
    tipo_ocorrencia = tipo_ocorrencia_factory.create(titulo="CARDÁPIO", edital=edital)
    assert tipo_ocorrencia.__str__() == "SME/02/24 - CARDÁPIO"


def test_tipo_ocorrencia_meta_modelo(tipo_ocorrencia_factory):
    tipo_ocorrencia = tipo_ocorrencia_factory.create()
    assert tipo_ocorrencia._meta.verbose_name == "Tipo de Ocorrência"
    assert tipo_ocorrencia._meta.verbose_name_plural == "Tipos de Ocorrência"


def test_validation_error_nao_eh_imr_pontuacao_tolerancia_preenchidos():
    data = {"eh_imr": False, "pontuacao": 1, "tolerancia": 1}
    form = TipoOcorrenciaForm(data=data)

    assert form.is_valid() is False
    assert form.errors["pontuacao"] == ["Pontuação só deve ser preenchida se for IMR."]
    assert form.errors["tolerancia"] == [
        "Tolerância só deve ser preenchida se for IMR."
    ]


def test_validation_error_eh_imr_pontuacao_tolerancia_nao_preenchidos():
    data = {"eh_imr": True, "pontuacao": None, "tolerancia": None}
    form = TipoOcorrenciaForm(data=data)

    assert form.is_valid() is False
    assert form.errors["pontuacao"] == ["Pontuação deve ser preenchida se for IMR."]
    assert form.errors["tolerancia"] == ["Tolerância deve ser preenchida se for IMR."]


def test_validation_faixa_pontuacao_imr_intervalo_existente(faixa_pontuacao_factory):
    faixa_pontuacao_factory.create(pontuacao_minima=5, pontuacao_maxima=10)

    data = {"pontuacao_minima": 1, "pontuacao_maxima": 4, "porcentagem_desconto": 1}
    form = FaixaPontuacaoIMRForm(data=data)

    assert form.is_valid() is True


def test_validation_error_faixa_pontuacao_imr_pontuacao_minima_intervalo_existente(
    faixa_pontuacao_factory,
):
    faixa_pontuacao_factory.create(pontuacao_minima=5, pontuacao_maxima=10)

    data = {"pontuacao_minima": 1, "pontuacao_maxima": 5, "porcentagem_desconto": 1}
    form = FaixaPontuacaoIMRForm(data=data)

    assert form.is_valid() is False
    assert form.errors["pontuacao_maxima"] == [
        "Esta pontuação máxima já se encontra dentro de outra faixa."
    ]


def test_validation_error_faixa_pontuacao_imr_pontuacao_maxima_intervalo_existente(
    faixa_pontuacao_factory,
):
    faixa_pontuacao_factory.create(pontuacao_minima=5, pontuacao_maxima=10)

    data = {"pontuacao_minima": 10, "pontuacao_maxima": 15, "porcentagem_desconto": 1}
    form = FaixaPontuacaoIMRForm(data=data)

    assert form.is_valid() is False
    assert form.errors["pontuacao_minima"] == [
        "Esta pontuação mínima já se encontra dentro de outra faixa."
    ]
