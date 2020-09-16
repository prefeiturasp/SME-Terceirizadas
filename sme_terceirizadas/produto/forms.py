from django import forms

from ..dados_comuns.fluxo_status import HomologacaoProdutoWorkflow
from .models import Fabricante, Marca


class ProdutoPorParametrosForm(forms.Form):
    uuid = forms.UUIDField(required=False)
    nome_fabricante = forms.CharField(required=False)
    nome_marca = forms.CharField(required=False)
    nome_produto = forms.CharField(required=False)
    nome_terceirizada = forms.CharField(required=False)
    data_inicial = forms.DateField(required=False)
    data_final = forms.DateField(required=False)
    status = forms.MultipleChoiceField(
        required=False,
        choices=[(str(state), state) for state in HomologacaoProdutoWorkflow.states]
    )


class ProdutoJaExisteForm(forms.Form):
    fabricante = forms.ModelChoiceField(Fabricante.objects.all(), to_field_name='uuid')
    marca = forms.ModelChoiceField(Marca.objects.all(), to_field_name='uuid')
    nome = forms.CharField()
