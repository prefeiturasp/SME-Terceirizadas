from django.db import models


class TemLabelDeTiposDeAlimentacao(models.Model):
    pass

    @property
    def label(self):
        label = ''
        for tipo_alimentacao in self.tipos_alimentacao.all():
            if len(label) == 0:
                label += tipo_alimentacao.nome
            else:
                label += f' e {tipo_alimentacao.nome}'
        return label
