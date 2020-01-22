from django import forms

from ..escola.models import DiretoriaRegional, Escola
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


class SolicitacoesAtivasInativasPorAlunoForm(forms.Form):
    escola = forms.ModelChoiceField(
        required=False,
        queryset=Escola.objects.all()
    )
    dre = forms.ModelChoiceField(
        required=False,
        queryset=DiretoriaRegional.objects.all()
    )
