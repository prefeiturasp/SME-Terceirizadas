import pytest
# from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.test import APITestCase

# from rest_framework.test import APIClient
from ..models import Usuario
from sme_terceirizadas.perfil.api.viewsets import UsuarioUpdateViewSet
from rest_framework.test import force_authenticate


pytestmark = pytest.mark.django_db


# def test_usuario_update_viewset():  # noqa
#     # view = UsuarioUpdateViewSet()
#     # request = request_factory.get("/fake-url/")
#     # request.usuario = usuario

#     # view.request = request

#     # assert view.get_success_url() == f"/cadastro/"

#     factory = APIRequestFactory()
#     usuario = Usuario.objects.create_user(email='admin@admin.com', password='adminadmin')  # noqa
#     usuario = Usuario.objects.get(email='admin@admin.com')
#     # view = AccountDetail.as_view()
#     view = UsuarioUpdateViewSet.as_view('/cadastro/')
#     request = factory.get('/cadastro/')
#     force_authenticate(request, user=usuario)
#     response = view(request)


# def test_usuario_update_viewset(client_autenticado):
#     response = client_autenticado.get('/cadastro/')
#     import ipdb
#     ipdb.set_trace()
#     assert response.status_code == status.HTTP_200_OK


class CheckUserViewTest(APITestCase):

    def test_usuario_update_viewset(self):
        usuario = Usuario.objects.create_user(
            email='admin@admin.com',
            password='adminadmin',
            nome='admin'
        )
        self.assertTrue(self.client.login(
            email='admin@admin.com',
            password='adminadmin',
            nome='admin'
        ))
        self.client.force_authenticate(usuario)
        response = self.client.get('/cadastro/')
        assert response.status_code == status.HTTP_200_OK
