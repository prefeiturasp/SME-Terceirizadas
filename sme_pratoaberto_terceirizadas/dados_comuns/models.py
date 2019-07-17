from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from django.db import models

from .models_abstract import (Descritivel, CriadoEm, TemChaveExterna)


class LogUsuario(Descritivel, CriadoEm, TemChaveExterna):
    """
        Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X a tarefa do tipo Z no dia tal, passando os dados W
    """
    # TODO: seria essa a melhor interação para registrar ações do usuario?
    # Lembrando que o objetivo final é fazer uma especie de auditoria...


class Contato(models.Model):
    telefone = models.CharField(max_length=10, validators=[MinLengthValidator(8)],
                                blank=True, null=True)
    telefone2 = models.CharField(max_length=10, validators=[MinLengthValidator(8)],
                                 blank=True, null=True)
    celular = models.CharField(max_length=11, validators=[MinLengthValidator(8)],
                               blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


class Endereco(models.Model):
    rua = models.CharField(max_length=200)
    cep = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10, blank=True, null=True)
