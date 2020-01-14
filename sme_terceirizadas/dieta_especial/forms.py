from django import forms

from .models import ClassificacaoDieta, SolicitacaoDietaEspecial, AlergiaIntolerancia

class AutorizaDietaEspecialForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoDietaEspecial
        fields = [
            'registro_funcional_nutricionista',
            'classificacao',
            'alergias_intolerancias'
        ]
