import pytest
from model_mommy import mommy


@pytest.fixture
def client_autenticado(client, django_user_model):
    email = 'test@test.com'
    password = 'bar'
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional='8888888')
    client.login(email=email, password=password)
    mommy.make('Vinculo', usuario=user)
    return client
