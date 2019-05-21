from model_utils import Choices
from model_utils.fields import StatusField

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, IntervaloDeDia
from sme_pratoaberto_terceirizadas.users.models import User


class AlteracaoCardapio(IntervaloDeDia, Describable):
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
