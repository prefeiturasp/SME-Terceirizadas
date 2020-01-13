from django.urls import path

from .relatorios import relatorio_kit_lanche_unificado

urlpatterns = [
    path(r'relatorio-kit-lanche-unificado', relatorio_kit_lanche_unificado, name='generate_pdf'),
]
