from django import forms


class CaixaAltaNomeForm(forms.ModelForm):

    def clean_nome(self):
        return self.cleaned_data['nome'].upper()
