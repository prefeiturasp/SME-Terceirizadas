from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, IntervaloDeDia, TemChaveExterna, \
    Motivos
from sme_pratoaberto_terceirizadas.school.models import School, SchoolAge, RegionalDirector
from sme_pratoaberto_terceirizadas.users.models import User


class AlteracaoCardapio(IntervaloDeDia, Describable, TemChaveExterna, Motivos):
    STATUS = Choices(

        # ESCOLA
        ('ESCOLA_SOLICITA', 'Nova solicitação pela Escola'),
        ('ESCOLA_RESOLICITA', 'Solicitação refeita pela Escola'),

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
    escola = models.ForeignKey(School, on_delete=models.DO_NOTHING)

    @classmethod
    def valida_existencia(cls, inicio, fim, escola_id):
        escola = cls.get_escola(escola_id)
        existe = cls.objects.filter(data_inicio=inicio, data_final=fim, escola=escola)
        if existe:
            return False
        return True

    @classmethod
    def get_escola(cls, id_escola):
        try:
            return School.objects.get(pk=id_escola)
        except ObjectDoesNotExist:
            return False

    @classmethod
    def get_usuarios_dre(cls, escola):
        dre = RegionalDirector.objects.filter(regional_director=escola.regional_director)
        return dre.values_list('users').all()


