import uuid

from django.core.validators import MinLengthValidator
from django.db import models


class LogSolicitacoesUsuario(models.Model):
    """Eventos de dados importantes para acompanhamento.

    Ex.: Fulano X  executou a atividade Y no objeto W no dia DDDDMMAA
    """

    (  # COMUNS AOS DOIS FLUXOS (PARTINDO DA ESCOLA E DA DRE)
        INICIO_FLUXO,
        CODAE_AUTORIZOU,
        TERCEIRIZADA_TOMOU_CIENCIA,
        TERCEIRIZADA_RECUSOU,
        CODAE_NEGOU,
        # ESPECIFICA DO PARTINDO DA DRE
        CODAE_PEDIU_REVISAO,
        DRE_REVISOU,

        # ESPECIFICA DO PARTINDO DA ESCOLA
        DRE_VALIDOU,
        DRE_PEDIU_REVISAO,
        DRE_NAO_VALIDOU,
        ESCOLA_REVISOU,

        # "BURLADO DO FLUXO", PODE SER CHAMADO A QUALQUER MOMENTO COM AS DEVIDAS RESTRIÇÕES
        ESCOLA_CANCELOU,
        DRE_CANCELOU,
    ) = range(13)

    STATUS_POSSIVEIS = (
        (INICIO_FLUXO, 'Solicitação Realizada'),
        (CODAE_AUTORIZOU, 'CODAE autorizou'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada tomou ciência'),
        (TERCEIRIZADA_RECUSOU, 'Terceirizada recusou'),
        (CODAE_NEGOU, 'CODAE negou'),
        (CODAE_PEDIU_REVISAO, 'CODAE pediu revisão'),
        (DRE_REVISOU, 'DRE revisou'),
        (DRE_VALIDOU, 'DRE validou'),
        (DRE_PEDIU_REVISAO, 'DRE pediu revisão'),
        (DRE_NAO_VALIDOU, 'DRE não validou'),
        (ESCOLA_REVISOU, 'Escola revisou'),
        (ESCOLA_CANCELOU, 'Escola cancelou'),
        (DRE_CANCELOU, 'DRE cancelou')
    )
    (  # DA ESCOLA
        SOLICITACAO_KIT_LANCHE_AVULSA,
        ALTERACAO_DE_CARDAPIO,
        SUSPENSAO_DE_CARDAPIO,
        INVERSAO_DE_CARDAPIO,
        INCLUSAO_ALIMENTACAO_NORMAL,
        INCLUSAO_ALIMENTACAO_CONTINUA,
        DIETA_ESPECIAL,
        # DA DRE
        SOLICITACAO_KIT_LANCHE_UNIFICADA
    ) = range(8)

    TIPOS_SOLICITACOES = (
        (SOLICITACAO_KIT_LANCHE_AVULSA, 'Solicitação de kit lanche avulsa'),
        (ALTERACAO_DE_CARDAPIO, 'Alteração de cardápio'),
        (SUSPENSAO_DE_CARDAPIO, 'Suspensão de cardápio'),
        (INVERSAO_DE_CARDAPIO, 'Inversão de cardápio'),
        (INCLUSAO_ALIMENTACAO_NORMAL, 'Inclusão de alimentação normal'),
        (INCLUSAO_ALIMENTACAO_CONTINUA, 'Inclusão de alimentação contínua'),
        (DIETA_ESPECIAL, 'Dieta Especial'),
        (SOLICITACAO_KIT_LANCHE_UNIFICADA, 'Solicitação de kit lanche unificada'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField('Criado em', editable=False, auto_now_add=True)
    descricao = models.TextField('Descricao', blank=True)
    justificativa = models.TextField('Justificativa', blank=True)
    status_evento = models.PositiveSmallIntegerField(choices=STATUS_POSSIVEIS)
    solicitacao_tipo = models.PositiveSmallIntegerField(choices=TIPOS_SOLICITACOES)
    uuid_original = models.UUIDField()
    usuario = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING)

    def __str__(self):
        return (f'{self.usuario} executou {self.get_status_evento_display()} '
                f'em {self.get_solicitacao_tipo_display()} no dia {self.criado_em}')


class Meta:
    ordering = ('criado_em',)


class Contato(models.Model):
    telefone = models.CharField(max_length=13, validators=[MinLengthValidator(8)],
                                blank=True)
    telefone2 = models.CharField(max_length=10, validators=[MinLengthValidator(8)],
                                 blank=True)
    celular = models.CharField(max_length=11, validators=[MinLengthValidator(8)],
                               blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f'{self.telefone}, {self.email}'


class TemplateMensagem(models.Model):
    """Tem um texto base e troca por campos do objeto que entra como parâmetro.

    Ex:
    Olá @nome, a Alteração de cardápio #@identificador solicitada por @requerinte está em situação @status.
    """

    ALTERACAO_CARDAPIO = 0
    INCLUSAO_ALIMENTACAO = 1
    INCLUSAO_ALIMENTACAO_CONTINUA = 2
    SUSPENSAO_ALIMENTACAO = 3
    SOLICITACAO_KIT_LANCHE_AVULSA = 4
    SOLICITACAO_KIT_LANCHE_UNIFICADA = 5
    INVERSAO_CARDAPIO = 6
    DIETA_ESPECIAL = 7

    CHOICES = (
        (ALTERACAO_CARDAPIO, 'Alteração de cardápio'),
        (INCLUSAO_ALIMENTACAO, 'Inclusão de alimentação'),
        (INCLUSAO_ALIMENTACAO_CONTINUA, 'Inclusão de alimentação contínua'),
        (SUSPENSAO_ALIMENTACAO, 'Suspensão de alimentação'),
        (SOLICITACAO_KIT_LANCHE_AVULSA, 'Solicitação de kit lanche avulsa'),
        (SOLICITACAO_KIT_LANCHE_UNIFICADA, 'Solicitação de kit lanche unificada'),
        (INVERSAO_CARDAPIO, 'Inversão de cardápio'),
        (DIETA_ESPECIAL, 'Dieta Especial')
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tipo = models.PositiveSmallIntegerField(choices=CHOICES, unique=True)
    assunto = models.CharField('Assunto', max_length=256, blank=True)
    template_html = models.TextField('Template', blank=True)

    def __str__(self):
        return f'{self.get_tipo_display()}'

    class Meta:
        verbose_name = 'Template de mensagem'
        verbose_name_plural = 'Template de mensagem'
