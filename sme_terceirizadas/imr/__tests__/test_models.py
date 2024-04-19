import pytest
from django.core.exceptions import ValidationError

from sme_terceirizadas.imr.admin import TipoOcorrenciaForm
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


def test_validation_error_eh_imr_pontuacao():
    data = {"eh_imr": False, "pontuacao": 1, "tolerancia": 1}
    form = TipoOcorrenciaForm(data=data)

    assert form.is_valid() is False
    assert form.errors["pontuacao"] == ["Pontuação só deve ser preenchida se for IMR."]
    assert form.errors["tolerancia"] == [
        "Tolerância só deve ser preenchida se for IMR."
    ]
