from django.core.validators import MinLengthValidator
from django.db import models

from ...dados_comuns.behaviors import ModeloBase


class Laboratorio(ModeloBase):
    nome = models.CharField('Nome', max_length=150, unique=True)
    cnpj = models.CharField('CNPJ', validators=[MinLengthValidator(14)], max_length=14)
    cep = models.CharField('CEP', max_length=8)
    logradouro = models.CharField('Logradouro', max_length=150)
    numero = models.CharField('Número', max_length=10)
    complemento = models.CharField('Complemento', max_length=50, blank=True)
    bairro = models.CharField('Bairro', max_length=150)
    cidade = models.CharField('Cidade', max_length=150)
    estado = models.CharField('Estado', max_length=150)
    credenciado = models.BooleanField('Está credenciado?', default=False)

    def __str__(self):
        return f'{self.nome}'

    class Meta:
        verbose_name = 'Laboratório'
        verbose_name_plural = 'Laboratórios'


class ContatoLaboratorio(ModeloBase):
    nome = models.CharField('Nome', max_length=150)
    telefone = models.CharField('Telefone', max_length=160)
    email = models.EmailField('E-mail')
    laboratorio = models.ForeignKey('Laboratorio', on_delete=models.CASCADE, related_name='contatos', blank=True,
                                    null=True)

    def __str__(self):
        return f'{self.nome}'

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
