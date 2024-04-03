from django import forms

from ..escola.models import DiretoriaRegional, Escola

class ControleSobrasForm(forms.Form):
    escola = forms.ModelChoiceField(
        required=False,
        queryset=Escola.objects.all(),
        to_field_name='uuid'
    )
    dre = forms.ModelChoiceField(
        required=False,
        queryset=DiretoriaRegional.objects.all(),
        to_field_name='uuid'
    )

class ControleSobrasRelatorioForm(forms.Form):
    escola = forms.ModelChoiceField(
        required=False,
        queryset=Escola.objects.all(),
        to_field_name='uuid'
    )
    dre = forms.ModelChoiceField(
        required=False,
        queryset=DiretoriaRegional.objects.all(),
        to_field_name='uuid'
    )
    data_inicial = forms.DateField(required=True)
    data_final = forms.DateField(required=True)

class ControleRestosForm(forms.Form):
    escola = forms.ModelChoiceField(
        required=False,
        queryset=Escola.objects.all(),
        to_field_name='uuid'
    )
    dre = forms.ModelChoiceField(
        required=False,
        queryset=DiretoriaRegional.objects.all(),
        to_field_name='uuid'
    )

class ControleRestosRelatorioForm(forms.Form):
    escola = forms.ModelChoiceField(
        required=False,
        queryset=Escola.objects.all(),
        to_field_name='uuid'
    )
    dre = forms.ModelChoiceField(
        required=False,
        queryset=DiretoriaRegional.objects.all(),
        to_field_name='uuid'
    )
    data_inicial = forms.DateField(required=True)
    data_final = forms.DateField(required=True)