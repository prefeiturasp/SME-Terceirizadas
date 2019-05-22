from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, IntervaloDeDia, TemChaveExterna
from sme_pratoaberto_terceirizadas.users.models import User


class AlteracaoCardapio(IntervaloDeDia, Describable, TemChaveExterna):
    STATUS = Choices(('SALVO', 'Salvo'),
                     ('A_VALIDAR', 'A validar'),
                     ('CONFIRMADO', 'Confirmado'),
                     ('A_VISUALIZAR', 'A visualizar'),
                     ('A_APROVAR', 'A aprovar'),
                     ('A_EDITAR', 'A editar'),
                     ('NEGADO_PELA_CODAE', 'Negado pela CODAE'),
                     ('NEGADO_PELA_COMPANHIA', 'Negado pela companhia'),
                     ('VISUALIZADO', 'Visualizado'))
    status = StatusField()
    # TODO criar o relacionamento...
    nome_escola = models.CharField('Nome da escola...', blank=True, null=True, max_length=256)
