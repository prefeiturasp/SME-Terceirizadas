from django import forms
from django.core.exceptions import ValidationError

from sme_terceirizadas.recebimento.models import QuestaoConferencia


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = QuestaoConferencia
        fields = "__all__"
        widgets = {
            "questao": forms.TextInput(
                attrs={
                    "oninput": "this.value = this.value.toUpperCase();",
                    "size": "100",
                }
            ),
        }

    def clean(self):
        posicao = self.cleaned_data["posicao"]
        tipo_questao = self.cleaned_data["tipo_questao"]
        if posicao is not None and tipo_questao:
            qs = QuestaoConferencia.objects.filter(
                posicao=posicao, tipo_questao__contains=tipo_questao
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        "posicao": "Já existe uma pergunta com essa posição para este tipo de questão."
                    }
                )
