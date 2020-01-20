from django import forms

from .models import SolicitacaoDietaEspecial


class AutorizaDietaEspecialForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoDietaEspecial
        fields = [
            'registro_funcional_nutricionista',
            'classificacao',
            'alergias_intolerancias'
        ]


class NegaDietaEspecialForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoDietaEspecial
        fields = [
            'justificativa_negacao',
            'motivo_negacao',
            'registro_funcional_nutricionista'
        ]
