from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('cadastro', viewsets.UsuarioUpdateViewSet, 'Cadastro de Usuários')
router.register('usuarios', viewsets.UsuarioViewSet, 'Usuários')
router.register('perfis', viewsets.PerfilViewSet, 'Perfis')
router.register('confirmar_email/(?P<uuid>[^/]+)/(?P<confirmation_key>[^/]+)',
                viewsets.UsuarioConfirmaEmailViewSet, 'Confirmar E-mail')

urlpatterns = [
    path(
        'exportar_planilha_importacao_usuarios_perfil_codae/',
        viewsets.exportar_planilha_importacao_usuarios_perfil_codae,
        name='exportar_planilha_importacao_usuarios_perfil_codae'
    ),
    path(
        'exportar_planilha_importacao_usuarios_perfil_escola/',
        viewsets.exportar_planilha_importacao_usuarios_perfil_escola,
        name='exportar_planilha_importacao_usuarios_perfil_escola'
    ),
    path(
        'exportar_planilha_importacao_usuarios_perfil_dre/',
        viewsets.exportar_planilha_importacao_usuarios_perfil_dre,
        name='exportar_planilha_importacao_usuarios_perfil_dre'
    ),
    path('', include(router.urls))
]
