import pytest

pytestmark = pytest.mark.django_db


def test_usuario_serializer(usuario_serializer):
    assert usuario_serializer.data is not None
