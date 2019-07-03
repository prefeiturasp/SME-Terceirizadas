from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .models_abstract import (Descritivel, CriadoEm, Nomeavel, TemChaveExterna)


class LogUsuario(Descritivel, CriadoEm, TemChaveExterna):
    """
        Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X a tarefa do tipo Z no dia tal, passando os dados W
    """
    # TODO: seria essa a melhor interação para registrar ações do usuario?
    # Lembrando que o objetivo final é fazer uma especie de auditoria...


class DiaSemana(TemChaveExterna):
    """
        Seg a Dom...
    """
    nome = models.CharField("Nome", blank=True, null=True, max_length=20, unique=True)
    numero = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], unique=True)

    class Meta:
        verbose_name = "Dia da semana"
        verbose_name_plural = "Dias da semana"

    def __str__(self):
        return '{}: {}'.format(self.numero, self.nome)


class DiasUteis(object):
    # TODO: Qual o objetivo dessa classe?
    def __init__(self, **kwargs):
        for campo in ('data_cinco_dias_uteis', 'data_dois_dias_uteis'):
            setattr(self, campo, kwargs.get(campo, None))
