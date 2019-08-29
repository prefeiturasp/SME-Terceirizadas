import datetime
import uuid

import xworkflows
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_xworkflows import models as xwf_models

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje
from sme_pratoaberto_terceirizadas.perfil import models as models_perfil
from .fluxo_status import (
    PedidoAPartirDaEscolaWorkflow,
    PedidoAPartirDaDiretoriaRegionalWorkflow,
    InformativoPartindoDaEscolaWorkflow
)
from .models import LogSolicitacoesUsuario
from .utils import enviar_notificacao_e_email


class Iniciais(models.Model):
    iniciais = models.CharField("Iniciais", blank=True, null=True, max_length=10)

    class Meta:
        abstract = True


class Descritivel(models.Model):
    descricao = models.TextField("Descricao", blank=True, null=True)

    class Meta:
        abstract = True


class Nomeavel(models.Model):
    nome = models.CharField("Nome", blank=True, null=True, max_length=50)

    class Meta:
        abstract = True


class Motivo(models.Model):
    motivo = models.TextField("Motivo", blank=True, null=True)

    class Meta:
        abstract = True


class Ativavel(models.Model):
    ativo = models.BooleanField("Está ativo?", default=True)

    class Meta:
        abstract = True


class CriadoEm(models.Model):
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)

    class Meta:
        abstract = True


class IntervaloDeTempo(models.Model):
    data_hora_inicial = models.DateTimeField("Data/hora inicial")
    data_hora_final = models.DateTimeField("Data/hora final")

    class Meta:
        abstract = True


class IntervaloDeDia(models.Model):
    data_inicial = models.DateField("Data inicial")
    data_final = models.DateField("Data final")

    class Meta:
        abstract = True


class TemData(models.Model):
    data = models.DateField("Data")

    class Meta:
        abstract = True


class TemChaveExterna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class DiasSemana(models.Model):
    SEGUNDA = 0
    TERCA = 1
    QUARTA = 2
    QUINTA = 3
    SEXTA = 4
    SABADO = 5
    DOMINGO = 6

    DIAS = (
        (SEGUNDA, 'Segunda'),
        (TERCA, 'Terça'),
        (QUINTA, 'Quarta'),
        (QUARTA, 'Quinta'),
        (SEXTA, 'Sexta'),
        (SABADO, 'Sábado'),
        (DOMINGO, 'Domingo'),
    )

    dias_semana = ArrayField(
        models.PositiveSmallIntegerField(choices=DIAS,
                                         default=[],
                                         null=True, blank=True
                                         )
    )

    def dias_semana_display(self):
        result = ''
        choices = dict(self.DIAS)
        for index, value in enumerate(self.dias_semana):
            result += "{0}".format(choices[value])
            if not index == len(self.dias_semana) - 1:
                result += ', '
        return result

    class Meta:
        abstract = True


class TempoPasseio(models.Model):
    QUATRO = 0
    CINCO_A_SETE = 1
    OITO_OU_MAIS = 2

    HORAS = (
        (QUATRO, 'Quatro horas'),
        (CINCO_A_SETE, 'Cinco a sete horas'),
        (OITO_OU_MAIS, 'Oito horas'),
    )
    tempo_passeio = models.PositiveSmallIntegerField(choices=HORAS,
                                                     null=True, blank=True)

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaEscolaWorkflow

    status = xwf_models.StateField(workflow_class)

    def cancelar_pedido_48h_antes(self, user, notificar=True):
        # TODO: verificar o campo de data do pedido, se tiver no intervalo altera o status
        # não faz nada caso contrario
        # TODO, disparar erro InvalidTransitionError caso de errado...
        self.status = self.workflow_class.ESCOLA_CANCELA_48H_ANTES

    def cancelamento_automatico_apos_vencimento(self):
        """
        Chamado automaticamente quando o pedido já passou do dia de atendimento e não chegou ao fim do fluxo
        """
        self.status = self.workflow_class.CANCELAMENTO_AUTOMATICO

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status == self.workflow_class.DRE_A_VALIDAR

    @property
    def ta_na_escola(self):
        return self.status in [self.workflow_class.RASCUNHO,
                               self.workflow_class.DRE_PEDE_ESCOLA_REVISAR]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.DRE_APROVADO

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_APROVADO

    @property
    def partes_interessadas_inicio_fluxo(self):
        """

        """
        dre = self.escola.diretoria_regional
        usuarios_dre = dre.usuarios.all()
        return usuarios_dre

    @property
    def partes_interessadas_dre_aprovou(self):
        # TODO: filtrar usuários CODAE
        usuarios_codae = models_perfil.Usuario.objects.filter()
        return usuarios_codae

    @property
    def partes_interessadas_codae_aprovou(self):
        # TODO: filtrar usuários Terceirizadas
        usuarios_terceirizadas = models_perfil.Usuario.objects.filter()
        return usuarios_terceirizadas

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: filtrar usuários Escolas
        usuarios_terceirizadas = models_perfil.Usuario.objects.filter()
        return usuarios_terceirizadas

    @property
    def template_mensagem(self):
        raise NotImplementedError('Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    def salvar_log_transicao(self, status_evento, usuario):
        raise NotImplementedError('Deve criar um método salvar_log_transicao')

    #
    # Esses hooks são chamados automaticamente após a
    # transition do status ser chamada.
    # Ex. >>> alimentacao_continua.inicia_fluxo(param1, param2, key1='val')
    #

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto, corpo = self.template_mensagem
        enviar_notificacao_e_email(sender=user,
                                   recipients=self.partes_interessadas_inicio_fluxo,
                                   short_desc=assunto,
                                   long_desc=corpo)
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)

    @xworkflows.after_transition('dre_aprovou')
    def _dre_aprovou_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_dre_aprovou,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DRE_APROVOU,
                                      usuario=user)

    @xworkflows.after_transition('dre_pediu_revisao')
    def _dre_pediu_revisao_hook(self, *args, **kwargs):
        print(f'Notificar partes interessadas nesse momento {self.escola}')

    @xworkflows.after_transition('escola_revisou')
    def _escola_revisou_hook(self, *args, **kwargs):
        print(f'Notificar partes interessadas nesse momento {self.escola.diretoria_regional}')

    @xworkflows.after_transition('codae_aprovou')
    def _codae_aprovou_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_codae_aprovou,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_APROVOU,
                                      usuario=user)

    @xworkflows.after_transition('codae_recusou')
    def _codae_recusou_hook(self, *args, **kwargs):
        print(f'Notificar partes interessadas nesse momento {self.escola.diretoria_regional}')
        print(f'Notificar partes interessadas nesse momento {self.escola}')

    @xworkflows.after_transition('terceirizada_tomou_ciencia')
    def _terceirizada_tomou_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_terceirizadas_tomou_ciencia,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMA_CIENCIA,
                                      usuario=user)

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaDiretoriaRegional(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaDiretoriaRegionalWorkflow
    status = xwf_models.StateField(workflow_class)

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status in [self.workflow_class.CODAE_PEDE_DRE_REVISAR,
                               self.workflow_class.RASCUNHO]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.CODAE_A_VALIDAR

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_APROVADO

    @property
    def partes_interessadas_codae_aprovou(self):
        # TODO: filtrar usuários Terceirizadas
        usuarios_terceirizadas = models_perfil.Usuario.objects.filter()
        return usuarios_terceirizadas

    @property
    def partes_interessadas_inicio_fluxo(self):
        """
        TODO: retornar usuários CODAE, esse abaixo é so pra passar...
        """
        dre = self.diretoria_regional
        usuarios_dre = dre.usuarios.all()
        return usuarios_dre

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: filtrar usuários Escolas
        usuarios_terceirizadas = models_perfil.Usuario.objects.filter()
        return usuarios_terceirizadas

    @property
    def template_mensagem(self):
        raise NotImplementedError('Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto, corpo = self.template_mensagem

        enviar_notificacao_e_email(sender=user,
                                   recipients=self.partes_interessadas_inicio_fluxo,
                                   short_desc=assunto,
                                   long_desc=corpo)
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)

    @xworkflows.after_transition('codae_aprovou')
    def _codae_aprovou_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_codae_aprovou,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_APROVOU,
                                      usuario=user)

    @xworkflows.after_transition('terceirizada_tomou_ciencia')
    def _terceirizada_tomou_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_terceirizadas_tomou_ciencia,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMA_CIENCIA,
                                      usuario=user)

    class Meta:
        abstract = True


class FluxoInformativoPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = InformativoPartindoDaEscolaWorkflow
    status = xwf_models.StateField(workflow_class)

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def partes_interessadas_informacao(self):
        """
        TODO: retornar usuários DRE, esse abaixo é so pra passar...
        """
        dre = self.escola.diretoria_regional
        usuarios_dre = dre.usuarios.all()
        return usuarios_dre

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: filtrar usuários Escolas
        usuarios_terceirizadas = models_perfil.Usuario.objects.filter()
        return usuarios_terceirizadas

    @property
    def template_mensagem(self):
        raise NotImplementedError('Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    @xworkflows.after_transition('informa')
    def _informa_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto, corpo = self.template_mensagem
        enviar_notificacao_e_email(sender=user,
                                   recipients=self.partes_interessadas_informacao,
                                   short_desc=assunto,
                                   long_desc=corpo)
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.SUSPENSAO_DE_CARDAPIO,
                                  usuario=user)

    @xworkflows.after_transition('terceirizada_tomou_ciencia')
    def _terceirizada_tomou_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user and kwargs.get('notificar', False):
            assunto, corpo = self.template_mensagem
            enviar_notificacao_e_email(sender=user,
                                       recipients=self.partes_interessadas_terceirizadas_tomou_ciencia,
                                       short_desc=assunto,
                                       long_desc=corpo)
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMA_CIENCIA,
                                      usuario=user)

    class Meta:
        abstract = True


class CriadoPor(models.Model):
    # TODO: futuramente deixar obrigatorio esse campo
    criado_por = models.ForeignKey('perfil.Usuario', on_delete=models.DO_NOTHING,
                                   null=True, blank=True)

    class Meta:
        abstract = True


class TemObservacao(models.Model):
    observacao = models.TextField("Observação", blank=True, null=True)

    class Meta:
        abstract = True


class TemIdentificadorExternoAmigavel(object):
    """
    Gera uma chave externa amigável, não única.
    Somente para identificar externamente.
    Obrigatoriamente o objeto deve ter um uuid
    """

    @property
    def id_externo(self):
        uuid = str(self.uuid)
        return uuid.upper()[:5]


class TemPrioridade(object):
    """
        Exibe uma descrição para a data caso seja prioridade
    """

    @property
    def prioridade(self):
        data = None
        descricao = ''
        prox_2_dias_uteis = obter_dias_uteis_apos_hoje(2)
        prox_3_dias_uteis = obter_dias_uteis_apos_hoje(3)
        prox_5_dias_uteis = obter_dias_uteis_apos_hoje(5)
        prox_6_dias_uteis = obter_dias_uteis_apos_hoje(6)
        hoje = datetime.date.today()
        if hasattr(self, "data"):
            data = self.data
        elif hasattr(self, "data_inicial"):
            data = self.data_inicial

        if hoje <= data <= prox_2_dias_uteis:
            descricao = 'PRIORITARIO'
        elif prox_5_dias_uteis >= data >= prox_3_dias_uteis:
            descricao = 'LIMITE'
        elif data >= prox_6_dias_uteis:
            descricao = 'REGULAR'
        return descricao


class Logs(object):
    @property
    def logs(self):
        return LogSolicitacoesUsuario.objects.filter(uuid_original=self.uuid)
