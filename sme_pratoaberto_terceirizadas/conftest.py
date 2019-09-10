import pytest


@pytest.fixture
def client_autenticado(client, django_user_model):
    email = 'test@test.com'
    password = 'bar'
    django_user_model.objects.create_user(password=password, email=email)
    client.login(email=email, password=password)

    return client
