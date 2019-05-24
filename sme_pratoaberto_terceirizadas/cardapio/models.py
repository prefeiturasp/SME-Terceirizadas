from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, IntervaloDeDia, TemChaveExterna
from sme_pratoaberto_terceirizadas.school.models import School, SchoolAge
from sme_pratoaberto_terceirizadas.users.models import User


class AlteracaoCardapio(IntervaloDeDia, Describable, TemChaveExterna):
    STATUS = Choices(
        # DRE
        ('DRE_A_VALIDAR', 'A validar pela DRE'),  # IMEDIATAMENTE ENTRA NESSE APOS CRIAR
        ('DRE_APROVADO', 'Aprovado pela DRE'),  # CODAE RECEBE
        ('DRE_REPROVADO', 'Reprovado pela DRE'),  # ESCOLA PODE EDITAR

        # CODAE
        ('CODAE_A_VALIDAR', 'A validar pela CODAE'),  # QUANDO A DRE VALIDA
        ('CODAE_APROVADO', 'Aprovado pela CODAE'),  # CODAE RECEBE
        ('CODAE_REPROVADO', 'Reprovado pela CODAE'),  # CODAE REPROVA FIM DE FLUXO

        # TERCEIRIZADA
        ('TERCEIRIZADA_A_VISUALIZAR', 'Terceirizada a visualizar'),
        ('TERCEIRIZADA_A_VISUALIZADO', 'Terceirizada visualizado')  # TOMOU CIENCIA, TODOS DEVEM FICAR SABENDO...
    )
    status = StatusField()
    idade = models.ForeignKey(SchoolAge, on_delete=models.DO_NOTHING)
