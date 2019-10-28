import pytest

pytestmark = pytest.mark.django_db


def test_vinculo_instituto_serializer(vinculo_instituto_serializer):
    assert vinculo_instituto_serializer.data is not None


def test_escola_simplissima_serializer(escola_simplissima_serializer):
    assert escola_simplissima_serializer.data is not None
