from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_status(value):
    if value != 'ativo' and value != 'suspenso':
        raise ValidationError(
            _('Status %(status)s inválido. O status tem que ser ou "ativo" ou "suspenso".'),
            params={'value': value},
        )

class ProdutoPorParametrosForm(forms.Form):
    nome_fabricante = forms.CharField(required=False)
    nome_marca = forms.CharField(required=False)
    nome_produto = forms.CharField(required=False)
    nome_terceirizada = forms.CharField(required=False)
    data_inicial = forms.DateField(required=False)
    data_final = forms.DateField(required=False)
    status = forms.CharField(required=False, validators=[validate_status])
