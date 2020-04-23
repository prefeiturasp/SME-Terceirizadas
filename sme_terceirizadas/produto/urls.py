from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('produtos', viewsets.ProdutoViewSet, 'Produtos')
router.register('informacoes-nutricionais', viewsets.InformacaoNutricionalViewSet, 'Informações Nutricionais')
router.register('protocolo-dieta-especial', viewsets.ProtocoloDeDietaEspecialViewSet, 'Protocolo Dieta Especial')
router.register('fabricantes', viewsets.FabricanteViewSet, 'Fabricantes')
router.register('marcas', viewsets.MarcaViewSet, 'Marcas')

urlpatterns = [
    path('', include(router.urls)),
]
