import uuid

from django.core.validators import MinLengthValidator
from django.db import models


class LogSolicitacoesUsuario(models.Model):
    """
        Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X  executou a atividade Y no objeto W no dia DDDDMMAA
    """

    (  # COMUNS AOS DOIS FLUXOS (PARTINDO DA ESCOLA E DA DRE)
        INICIO_FLUXO,
        CODAE_APROVOU,
        TERCEIRIZADA_TOMA_CIENCIA,
        CODAE_CANCELOU_PEDIDO,
        # ESPECIFICA DO PARTINDO DA DRE
        CODAE_PEDE_REVISAO,
        DRE_REVISOU,
        # ESPECIFICA DO PARTINDO DA ESCOLA
        DRE_APROVOU,
        DRE_PEDIU_REVISAO,
        DRE_CANCELOU_PEDIDO,
        ESCOLA_REVISOU
    ) = range(10)

    STATUS_POSSIVEIS = (
        (INICIO_FLUXO, 'Inicio de fluxo'),
        (CODAE_APROVOU, 'CODAE aprovou'),
        (TERCEIRIZADA_TOMA_CIENCIA, 'Terceirizada toma ciência'),
        (CODAE_CANCELOU_PEDIDO, 'CODAE cancelou pedido'),
        (CODAE_PEDE_REVISAO, 'CODAE pede revisão'),
        (DRE_REVISOU, 'DRE revisou'),
        (DRE_APROVOU, 'DRE aprovou'),
        (DRE_PEDIU_REVISAO, 'DRE pediu revisão'),
        (DRE_CANCELOU_PEDIDO, 'DRE cancelou pedido'),
        (ESCOLA_REVISOU, 'Escola revisou'),
    )
    (  # DA ESCOLA
        SOLICITACAO_KIT_LANCHE_AVULSA,
        ALTERACAO_DE_CARDAPIO,
        SUSPENSAO_DE_CARDAPIO,
        INVERSAO_DE_CARDAPIO,
        INCLUSAO_ALIMENTACAO_NORMAL,
        INCLUSAO_ALIMENTACAO_CONTINUA,
        # DA DRE
        SOLICITACAO_KIT_LANCHE_UNIFICADA
    ) = range(7)

    TIPOS_SOLICITACOES = (
        (SOLICITACAO_KIT_LANCHE_AVULSA, 'Solicitação de kit lanche avulsa'),
        (ALTERACAO_DE_CARDAPIO, 'Alteração de cardápio'),
        (SUSPENSAO_DE_CARDAPIO, 'Suspensão de cardápio'),
        (INVERSAO_DE_CARDAPIO, 'Inversão de cardápio'),
        (INCLUSAO_ALIMENTACAO_NORMAL, 'Inclusão de alimentação normal'),
        (INCLUSAO_ALIMENTACAO_CONTINUA, 'Inclusão de alimentação contínua'),
        (SOLICITACAO_KIT_LANCHE_UNIFICADA, 'Solicitação de kit lanche unificada'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)
    descricao = models.TextField("Descricao", blank=True, null=True)
    status_evento = models.PositiveSmallIntegerField(choices=STATUS_POSSIVEIS)
    solicitacao_tipo = models.PositiveSmallIntegerField(choices=TIPOS_SOLICITACOES)
    uuid_original = models.UUIDField()
    usuario = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.usuario} executou {self.get_status_evento_display()} em " \
            f"{self.get_solicitacao_tipo_display()} no dia {self.criado_em}"


class Contato(models.Model):
    telefone = models.CharField(max_length=10, validators=[MinLengthValidator(8)],
                                blank=True, null=True)
    telefone2 = models.CharField(max_length=10, validators=[MinLengthValidator(8)],
                                 blank=True, null=True)
    celular = models.CharField(max_length=11, validators=[MinLengthValidator(8)],
                               blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f'{self.telefone}, {self.email}'


class Endereco(models.Model):
    rua = models.CharField(max_length=200)
    cep = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.rua}, {self.numero}'


class TemplateMensagem(models.Model):
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tipo = models.PositiveSmallIntegerField(choices=CHOICES, unique=True)
    assunto = models.CharField('Assunto', max_length=256, null=True, blank=True)
    template_html = models.TextField('Template', null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()}"

    class Meta:
        verbose_name = "Template de mensagem"
        verbose_name_plural = "Template de mensagem"
