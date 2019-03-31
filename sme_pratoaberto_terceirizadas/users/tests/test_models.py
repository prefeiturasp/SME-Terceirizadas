import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestUsers:

    def test_user_get_absolute_url(self, user: settings.AUTH_USER_MODEL):
        assert user.get_absolute_url() == f"/users/{user.username}/"
