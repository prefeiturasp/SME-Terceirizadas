import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestUsers:

    def test_user_get_absolute_url(self, user: settings.AUTH_USER_MODEL):
        assert user.get_absolute_url() == f"/users/{user.username}/"

    def test_new_user(self, django_user_model):
        self.user = django_user_model.objects.create(username="someone", is_nutritionist=True,
                                                     functional_register="etc", phone='phone',
                                                     password="something", mobile_phone='mob')
