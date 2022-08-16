import pytest

pytestmark = pytest.mark.django_db


def test_dia_sobremesa_doce_model(dia_sobremesa_doce):
    assert dia_sobremesa_doce.__str__() == '08/08/2022 - EMEF'
