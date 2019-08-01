from django.core.validators import MinLengthValidator
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


class TemplateMensagem(TemChaveExterna):
    """
        Tem um texto base e troca por campos do objeto que entra como parâmetro
        Ex:  Olá @nome, a Alteração de cardápio #@identificador solicitada
        por @requerinte está em situação @status.
    """
    ALTERACAO_CARDAPIO = 0
    INCLUSAO_ALIMENTACAO = 1
    INCLUSAO_ALIMENTACAO_CONTINUA = 2
    SUSPENSAO_ALIMENTACAO = 3
    SOLICITACAO_KIT_LANCHE_AVULSA = 4
    SOLICITACAO_KIT_LANCHE_UNIFICADA = 5
    INVERSAO_CARDAPIO = 6

    CHOICES = (
        (ALTERACAO_CARDAPIO, 'Alteração de cardápio'),
        (INCLUSAO_ALIMENTACAO, 'Inclusão de alimentação'),
        (INCLUSAO_ALIMENTACAO_CONTINUA, 'Inclusão de alimentação contínua'),
        (SUSPENSAO_ALIMENTACAO, 'Suspensão de alimentação'),
        (SOLICITACAO_KIT_LANCHE_AVULSA, 'Solicitação de kit lanche avulsa'),
        (SOLICITACAO_KIT_LANCHE_UNIFICADA, 'Solicitação de kit lanche unificada'),
        (INVERSAO_CARDAPIO, 'Inversão de cardápio')
    )
    tipo = models.PositiveSmallIntegerField(choices=CHOICES, unique=True)
    assunto = models.CharField('Assunto', max_length=256, null=True, blank=True)
    template_html = models.TextField('Template', null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()}"

    class Meta:
        verbose_name = "Template de mensagem"
        verbose_name_plural = "Template de mensagem"
