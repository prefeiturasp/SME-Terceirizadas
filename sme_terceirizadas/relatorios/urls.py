from django.urls import path

from .relatorios import generate_pdf

urlpatterns = [
    path(r'xxx', generate_pdf, name='generate_pdf'),
]
